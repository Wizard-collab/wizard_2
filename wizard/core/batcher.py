# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import copy
import logging

# Wizard modules
from wizard.core import assets
from wizard.core import project
from wizard.core import launch_batch
from wizard.core import tools
from wizard.core import team_client
from wizard.core import environment

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# Block types (must match the UI block type names)
# ----------------------------------------------------------------------
STAGE_SELECTION = 'stage_selection'
COMMENT = 'comment'
IMPORT_ALL = 'import_all'
UPDATE_ALL = 'update_all'
BATCH_EXPORT_DATA = 'batch_export_data'
BATCH_VIDEO = 'batch_video'
OPEN_AND_SAVE = 'open_and_save'
CREATE_REFERENCE = 'create_reference'
ASSEMBLY = 'assembly'
CODE = 'code'
CATEGORY_SELECTION = 'category_selection'
DOMAIN_SELECTION = 'domain_selection'
# Legacy type (now split into import_all + update_all)
IMPORT_AND_UPDATE_ALL = 'import_and_update_all'

# Variable types used for the typed data-flow (iOS-shortcuts style).
TYPE_STAGE_ID = 'stage_id'
TYPE_COMMENT = 'comment'
TYPE_BOOLEAN = 'boolean'
TYPE_COUNT = 'count'
TYPE_ANY = '*'

# Categories (must match the UI block categories)
CATEGORY_FILTER = 'filter'
CATEGORY_ARGUMENT = 'argument'
CATEGORY_WIZARD_ACTION = 'wizard_action'
CATEGORY_PROCESS = 'process'

_CATEGORY_ORDER = {
    CATEGORY_FILTER: 0,
    CATEGORY_ARGUMENT: 1,
    CATEGORY_WIZARD_ACTION: 2,
    CATEGORY_PROCESS: 3,
}

# Block type -> category (so the interpreter can order execution)
_TYPE_CATEGORIES = {
    STAGE_SELECTION: CATEGORY_FILTER,
    CATEGORY_SELECTION: CATEGORY_FILTER,
    DOMAIN_SELECTION: CATEGORY_FILTER,
    COMMENT: CATEGORY_ARGUMENT,
    IMPORT_ALL: CATEGORY_ARGUMENT,
    UPDATE_ALL: CATEGORY_ARGUMENT,
    IMPORT_AND_UPDATE_ALL: CATEGORY_ARGUMENT,
    BATCH_EXPORT_DATA: CATEGORY_PROCESS,
    BATCH_VIDEO: CATEGORY_PROCESS,
    OPEN_AND_SAVE: CATEGORY_PROCESS,
    CREATE_REFERENCE: CATEGORY_WIZARD_ACTION,
    ASSEMBLY: CATEGORY_WIZARD_ACTION,
    CODE: CATEGORY_WIZARD_ACTION,
}

# ----------------------------------------------------------------------
# Block I/O signatures.
#
# Each block declares the typed inputs it READS (bound by the user to an
# upstream variable) and the typed outputs it WRITES (given an auto-generated
# variable name that downstream blocks can select).
# Signature format: list of (variable_name, type) pairs. TYPE_ANY ('*') is
# used by the code block to read/write the whole context.
# ----------------------------------------------------------------------
_BLOCK_SIGNATURES = {
    STAGE_SELECTION: {
        'inputs': [],
        'outputs': [('stages', TYPE_STAGE_ID)],
    },
    CATEGORY_SELECTION: {
        'inputs': [],
        'outputs': [('stages', TYPE_STAGE_ID)],
    },
    DOMAIN_SELECTION: {
        'inputs': [],
        'outputs': [('stages', TYPE_STAGE_ID)],
    },
    COMMENT: {
        'inputs': [],
        'outputs': [('comment', TYPE_COMMENT)],
    },
    IMPORT_ALL: {
        'inputs': [],
        'outputs': [('value', TYPE_BOOLEAN)],
    },
    UPDATE_ALL: {
        'inputs': [],
        'outputs': [('value', TYPE_BOOLEAN)],
    },
    IMPORT_AND_UPDATE_ALL: {
        'inputs': [],
        'outputs': [('import_all', TYPE_BOOLEAN),
                    ('update_all', TYPE_BOOLEAN)],
    },
    CREATE_REFERENCE: {
        # 'reference_selection' -> source stages whose exports are referenced,
        # 'stages'              -> target stages (where references are created).
        'inputs': [('reference_selection', TYPE_STAGE_ID),
                   ('stages', TYPE_STAGE_ID)],
        'outputs': [('references', TYPE_COUNT)],
    },
    ASSEMBLY: {
        'inputs': [('stages', TYPE_STAGE_ID)],
        'outputs': [('references', TYPE_COUNT)],
    },
    BATCH_EXPORT_DATA: {
        'inputs': [('stages', TYPE_STAGE_ID),
                   ('comment', TYPE_COMMENT),
                   ('import_all', TYPE_BOOLEAN),
                   ('update_all', TYPE_BOOLEAN)],
        'outputs': [],
    },
    BATCH_VIDEO: {
        'inputs': [('stages', TYPE_STAGE_ID),
                   ('comment', TYPE_COMMENT),
                   ('import_all', TYPE_BOOLEAN),
                   ('update_all', TYPE_BOOLEAN)],
        'outputs': [],
    },
    OPEN_AND_SAVE: {
        'inputs': [('stages', TYPE_STAGE_ID),
                   ('comment', TYPE_COMMENT),
                   ('import_all', TYPE_BOOLEAN),
                   ('update_all', TYPE_BOOLEAN)],
        'outputs': [],
    },
    CODE: {
        'inputs': [('*', TYPE_ANY)],
        'outputs': [('*', TYPE_ANY)],
    },
}


def get_block_io(type_name):
    """Return (inputs, outputs) signatures for a block type.

    Each signature is a list of (variable_name, type) tuples. Used by the UI
    to display the variable selectors and the produced variables.
    """
    sig = _BLOCK_SIGNATURES.get(type_name, {'inputs': [], 'outputs': []})
    return list(sig['inputs']), list(sig['outputs'])


def _block_handlers():
    """Map block type -> handler(input_values, data, variables)."""
    return {
        STAGE_SELECTION: _handle_stage_selection,
        CATEGORY_SELECTION: _handle_category_selection,
        DOMAIN_SELECTION: _handle_domain_selection,
        COMMENT: _handle_comment,
        IMPORT_ALL: _handle_import_all,
        UPDATE_ALL: _handle_update_all,
        IMPORT_AND_UPDATE_ALL: _handle_import_and_update_all,
        BATCH_EXPORT_DATA: _handle_batch_export_data,
        BATCH_VIDEO: _handle_batch_video,
        OPEN_AND_SAVE: _handle_open_and_save,
        CREATE_REFERENCE: _handle_create_reference,
        ASSEMBLY: _handle_assembly,
        CODE: _handle_code,
    }


# ----------------------------------------------------------------------
# Typed variable assignment
# ----------------------------------------------------------------------
def auto_assign_variables(blocks):
    """Walk the blocks and deterministically assign:
      - a unique output variable name for every produced output,
      - a default upstream binding for every input (if none/outdated).

    The assignments are written back into each block's ``data['inputs']`` and
    ``data['outputs']`` so they persist. Returns a list with one entry per
    block: {'available': [[name, type], ...], 'inputs': {...}, 'outputs': {...}}
    where ``available`` are the upstream variables visible to that block.
    """
    results = []
    available = []          # [[var_name, type], ...] produced by earlier blocks
    for block in blocks:
        if not isinstance(block, dict):
            results.append({'available': [list(p) for p in available],
                            'inputs': {}, 'outputs': {}})
            continue
        block_type = block.get('type', '')
        sig = _BLOCK_SIGNATURES.get(
            block_type, {'inputs': [], 'outputs': []})
        data = block.get('data')
        if not isinstance(data, dict):
            data = {}
            block['data'] = data
        curr_inputs = data.get('inputs')
        if not isinstance(curr_inputs, dict):
            curr_inputs = {}
        curr_outputs = data.get('outputs')
        if not isinstance(curr_outputs, dict):
            curr_outputs = {}

        upstream_names = [name for name, _ in available]
        for name, typ in sig['inputs']:
            if typ == TYPE_ANY:
                curr_inputs.pop(name, None)
                continue
            var = curr_inputs.get(name)
            if var is None or not _is_valid_binding(var, typ, available):
                var = _last_available(typ, available)
            curr_inputs[name] = var

        out_assign = {}
        used_names = {name for name, _ in available}
        for name, typ in sig['outputs']:
            if typ == TYPE_ANY:
                continue
            var = curr_outputs.get(name)
            # Only keep an existing name if it is still unique; otherwise
            # generate a fresh one above the current max (so two filters get
            # distinct, sequential names like stage_id_1 / stage_id_2).
            if not var or var in used_names:
                var = _next_unique_var_name(typ, used_names)
            used_names.add(var)
            out_assign[name] = var
            curr_outputs[name] = var

        results.append({
            'available': [list(p) for p in available],
            'inputs': dict(curr_inputs),
            'outputs': dict(out_assign),
        })

        data['inputs'] = curr_inputs
        data['outputs'] = curr_outputs

        for name, typ in sig['outputs']:
            if typ != TYPE_ANY:
                available.append([curr_outputs[name], typ])

    return results


def _is_valid_binding(var_name, typ, available):
    for name, vtype in available:
        if name == var_name:
            return vtype == typ
    return False


def _last_available(typ, available):
    for var_name, vtype in reversed(available):
        if vtype == typ:
            return var_name
    return None


def _next_unique_var_name(typ, used_names):
    """Return the next unused ``{typ}_N`` name above the current max."""
    prefix = f"{typ}_"
    highest = 0
    for used in used_names:
        if used.startswith(prefix):
            try:
                highest = max(highest, int(used[len(prefix):]))
            except ValueError:
                pass
    return f"{typ}_{highest + 1}"


# ----------------------------------------------------------------------
# Execution
# ----------------------------------------------------------------------
def execute_sequence(sequence):
    """
    Interpret and execute a sequence.

    Args:
        sequence (dict): A sequence dict {
            'name': str,
            'blocks': [{'type': str, 'data': dict}, ...],
        }

    Blocks are walked in the order they appear. Each block reads its inputs
    from the typed ``variables`` dict through the variable bindings stored in
    ``data['inputs']``, calls its handler, and stores every produced output in
    ``variables`` under the auto-generated name in ``data['outputs']``.
    """
    if not isinstance(sequence, dict):
        logger.error("execute_sequence expects a sequence dict")
        return

    name = sequence.get('name', '')
    blocks = list(sequence.get('blocks', []))
    logger.info(f"Executing sequence '{name}' ({len(blocks)} blocks)")

    # First (re)compute the variable assignments so the saved bindings are
    # always consistent, even if a sequence file was hand-edited.
    auto_assign_variables(blocks)

    variables = {}
    handlers = _block_handlers()
    for block in blocks:
        if not isinstance(block, dict):
            continue
        block_type = block.get('type', '')
        block_data = block.get('data', {}) or {}
        sig = _BLOCK_SIGNATURES.get(
            block_type, {'inputs': [], 'outputs': []})
        handler = handlers.get(block_type)
        if handler is None:
            logger.warning(f"Unknown block type '{block_type}', skipping")
            continue

        # Resolve the typed inputs from the bound upstream variables.
        binding_in = block_data.get('inputs', {}) or {}
        input_values = {}
        for in_name, in_type in sig['inputs']:
            if in_type == TYPE_ANY:
                input_values[in_name] = variables
                continue
            var = binding_in.get(in_name)
            if var is None or var not in variables:
                input_values[in_name] = None
            else:
                input_values[in_name] = variables[var]

        logger.info(f"  -> processing block '{block_type}'")
        outputs = handler(input_values, block_data, variables)
        if not outputs:
            continue

        binding_out = block_data.get('outputs', {}) or {}
        for out_name, out_type in sig['outputs']:
            if out_type == TYPE_ANY:
                continue
            var = binding_out.get(out_name)
            if var is None:
                continue
            variables[var] = outputs.get(out_name)

    logger.info(f"Sequence '{name}' finished")


# ----------------------------------------------------------------------
# Handlers -- signature: (input_values, data, variables) -> {out: value}
# where 'variables' is the mutable shared dict (available for code blocks).
# ----------------------------------------------------------------------
def _handle_stage_selection(input_values, data, variables):
    """Filter block : produce the affected stages from a filter query."""
    query = data.get('filter', '') or ''
    matched_ids = get_matching_stage_ids(query)
    logger.info(f"Stage filter '{query}' matched {len(matched_ids)} stages")
    return {'stages': matched_ids}


def _handle_category_selection(input_values, data, variables):
    """Filter block : produce the stages of a category."""
    category_id = data.get('category', '')
    ids = _get_stages_in_category(category_id) if category_id else []
    logger.info(f"Category selection matched {len(ids)} stages")
    return {'stages': ids}


def _handle_domain_selection(input_values, data, variables):
    """Filter block : produce the stages of a domain."""
    domain_id = data.get('domain', '')
    ids = _get_stages_in_domain(domain_id) if domain_id else []
    logger.info(f"Domain selection matched {len(ids)} stages")
    return {'stages': ids}


def _get_stages_in_category(category_id):
    ids = []
    for asset_row in project.get_category_childs(category_id):
        for stage_row in project.get_asset_childs(asset_row['id']):
            ids.append(stage_row['id'])
    return ids


def _get_stages_in_domain(domain_id):
    ids = []
    for category_row in project.get_domain_childs(domain_id):
        ids.extend(_get_stages_in_category(category_row['id']))
    return ids


def _handle_comment(input_values, data, variables):
    """Argument block : produce the comment used for the export."""
    return {'comment': data.get('comment', '') or ''}


def _handle_import_all(input_values, data, variables):
    """Argument block : flag that process blocks must import all references."""
    return {'value': True}


def _handle_update_all(input_values, data, variables):
    """Argument block : flag that process blocks must update all references."""
    return {'value': True}


def _handle_import_and_update_all(input_values, data, variables):
    """Legacy block : produces BOTH import all and update all flags."""
    return {'import_all': True, 'update_all': True}


def _handle_batch_export_data(input_values, data, variables):
    """Process block : batch export of the (bound) affected stages."""
    _batch_process_stages(input_values.get('stages') or [],
                          batch_type='export',
                          import_all=1 if input_values.get('import_all') else 0,
                          update_all=1 if input_values.get('update_all') else 0,
                          comment=input_values.get('comment') or '')
    return {}


def _handle_batch_video(input_values, data, variables):
    """Process block : create a video for each (bound) affected stage."""
    _batch_process_stages(input_values.get('stages') or [],
                          batch_type='video',
                          import_all=1 if input_values.get('import_all') else 0,
                          update_all=1 if input_values.get('update_all') else 0,
                          comment=input_values.get('comment') or '')
    return {}


def _get_default_work_env_id(stage_id):
    stage_row = project.get_stage_data(stage_id)
    if not stage_row:
        return None
    default_variant_row = project.get_variant_data(
        stage_row.get('default_variant_id'))
    if not default_variant_row:
        return None
    default_work_env_row = project.get_work_env_data(
        default_variant_row.get('default_work_env_id'))
    if not default_work_env_row:
        return None
    return default_work_env_row['id']


def _handle_create_reference(input_values, data, variables):
    """Wizard-action block : create references to the exports of the selected
    source stages, into each stage provided as the target input.

    Source stages come from the 'reference_selection' input variable; if it is
    not bound, the block's own internal filter is used instead."""
    target_stage_ids = input_values.get('stages') or []
    source_stage_ids = input_values.get('reference_selection')
    if not source_stage_ids:
        query = data.get('filter', '') or ''
        source_stage_ids = (get_matching_stage_ids(query)
                            if query else target_stage_ids)
    if not target_stage_ids:
        logger.warning("No stage provided, skipping create reference")
        return {'references': 0}
    total = 0
    for target_stage_id in target_stage_ids:
        total += _create_references_for_target(target_stage_id,
                                               source_stage_ids)
    logger.info(f"Created {total} reference(s) in the wizard")
    return {'references': total}


def _create_references_for_target(target_stage_id, source_stage_ids):
    work_env_id = _get_default_work_env_id(target_stage_id)
    if not work_env_id:
        return 0
    count = 0
    for source_stage_id in source_stage_ids:
        export_rows = project.get_stage_export_childs(source_stage_id)
        for export_row in export_rows:
            export_version_id = project.get_default_export_version(
                export_row['id'], 'id')
            if export_version_id:
                assets.create_reference(work_env_id, export_version_id)
                count += 1
    return count


def _handle_assembly(input_values, data, variables):
    """Wizard-action block : reference the OTHER stages of the affected
    assets (assembly), like the lighting assembly script."""
    stage_ids = input_values.get('stages') or []
    if not stage_ids:
        logger.warning("No stage provided, skipping assembly")
        return {'references': 0}
    total = 0
    for stage_id in stage_ids:
        total += _create_sibling_references(stage_id)
    logger.info(f"Assembly: created {total} reference(s)")
    return {'references': total}


def _create_sibling_references(stage_id):
    stage_row = project.get_stage_data(stage_id)
    if not stage_row:
        return 0
    work_env_id = _get_default_work_env_id(stage_id)
    if not work_env_id:
        return 0
    asset_id = stage_row['asset_id']
    count = 0
    for other_stage_row in project.get_asset_childs(asset_id):
        name = other_stage_row['name']
        if name == stage_row['name'] or name == 'compositing':
            continue
        export_rows = project.get_stage_export_childs(other_stage_row['id'])
        for export_row in export_rows:
            export_version_id = project.get_default_export_version(
                export_row['id'], 'id')
            if export_version_id:
                assets.create_reference(work_env_id, export_version_id)
                count += 1
    return count


def _handle_code(input_values, data, variables):
    """Wizard-action block : run arbitrary Python code using the wizard
    public API (wapi) plus the running typed context."""
    code = data.get('code', '') or ''
    if not code.strip():
        logger.warning("Code block is empty, skipping")
        return {}
    logger.info("Executing code block")
    try:
        import wapi
    except Exception as e:
        logger.error(f"Could not import wapi: {e}")
        return {}
    api = {
        'wapi': wapi,
        'context': variables,
        'variables': variables,
        'logger': logger,
    }
    try:
        exec(code, api)
    except Exception as e:
        logger.error(f"Code block failed: {e}")
    return {}


def _handle_open_and_save(input_values, data, variables):
    """Process block : open each affected stage's work env, import & update
    all references if the bound flags are set, then save."""
    stages = input_values.get('stages') or []
    if not stages:
        logger.warning("No stage provided, skipping open and save")
        return {}
    comment = input_values.get('comment') or ''
    import_all = 1 if input_values.get('import_all') else 0
    update_all = 1 if input_values.get('update_all') else 0
    percent = 0.0
    percent_step = 100 / len(stages)
    for stage_id in stages:
        last_version_id = _get_default_last_version_id(stage_id)
        if not last_version_id:
            continue
        print(f"wizard_task_name:Open and save {_stage_label(stage_id)}")
        launch_batch.batch_export(
            last_version_id,
            {'batch_type': 'save',
             'import_all': import_all,
             'update_all': update_all,
             'comment': comment})
        tools.wait_for_child_processes()
        team_client.refresh_team(environment.get_team_dns())
        percent += percent_step
        print(f"wizard_task_percent:{percent}")
    return {}


# ----------------------------------------------------------------------
# Stage filtering (same keyword logic as the UI / tree search)
# ----------------------------------------------------------------------
def get_matching_stage_ids(query):
    """Return the list of stage ids matching a filter query.

    Supports the wizard syntax: '&' = AND keywords, '+' = OR set.
    """
    all_stages = project.get_all_stages()
    keywords_sets = query.split('+')
    stage_ids = []
    _ignored_keys = ('id', 'creation_time', 'creation_user', 'work_time',
                     'progress', 'estimated_time', 'default_variant_id',
                     'asset_id', 'domain_id')
    for keywords_set in keywords_sets:
        keywords = keywords_set.split('&')
        for stage_row in all_stages:
            row_cp = copy.deepcopy(stage_row)
            for key in _ignored_keys:
                row_cp.pop(key, None)
            values = [str(value) for value in row_cp.values()]
            data = (' ').join(values)
            if all(keyword.upper() in data.upper() for keyword in keywords):
                if stage_row['id'] not in stage_ids:
                    stage_ids.append(stage_row['id'])
    return stage_ids


# ----------------------------------------------------------------------
# Batch execution helpers
# ----------------------------------------------------------------------
def _batch_process_stages(stages_ids_list, batch_type='export',
                          import_all=0, update_all=0, comment=''):
    if not stages_ids_list:
        logger.warning("No stage selected, skipping batch process")
        return
    percent = 0.0
    percent_step = 100 / len(stages_ids_list)
    for stage_id in stages_ids_list:
        stage_row = project.get_stage_data(stage_id)
        if not stage_row:
            logger.info(f"Stage {stage_id} not found, skipping.")
            continue
        asset_row = project.get_asset_data(stage_row['asset_id'])
        default_variant_row = project.get_variant_data(
            stage_row.get('default_variant_id'))
        if not default_variant_row:
            logger.info(f"Default variant of {stage_row['name']} not found, "
                        "skipping.")
            continue
        default_work_env_row = project.get_work_env_data(
            default_variant_row.get('default_work_env_id'))
        if not default_work_env_row:
            logger.info(f"Default work environment of "
                        f"{stage_row['name']} not found, skipping.")
            continue

        last_version_id = _get_last_version_id(default_work_env_row['id'])
        if not last_version_id:
            logger.info(f"No work version found for "
                        f"{stage_row['name']}, skipping.")
            continue

        frange = [asset_row['inframe'], asset_row['outframe']]
        namespaces_list = _get_namespaces_list(default_work_env_row['id'],
                                               stage_row['name'],
                                               batch_type)

        settings_dic = dict()
        settings_dic['batch_type'] = batch_type
        settings_dic['import_all'] = import_all
        settings_dic['update_all'] = update_all
        settings_dic['refresh_assets'] = update_all  # backward compat
        settings_dic['frange'] = frange
        settings_dic['nspace_list'] = namespaces_list
        settings_dic['comment'] = comment
        settings_dic['stage_to_export'] = stage_row['name']

        action_label = 'Creating video' if batch_type == 'video' \
            else 'Exporting'
        print(f"wizard_task_name:{action_label} "
              f"{asset_row['name']}/{stage_row['name']}")

        launch_batch.batch_export(last_version_id, settings_dic)
        tools.wait_for_child_processes()
        team_client.refresh_team(environment.get_team_dns())
        percent += percent_step
        print(f"wizard_task_percent:{percent}")


def _get_namespaces_list(work_env_id, stage_name, batch_type):
    if batch_type == 'video':
        reference_types = ['camrig', 'camera']
    elif stage_name in ['animation', 'cfx']:
        reference_types = ['rigging']
    else:
        return []

    namespaces_list = []
    references_dic = assets.get_references_files(work_env_id)
    for reference_type in references_dic.keys():
        if reference_type not in reference_types:
            continue
        for reference_dic in references_dic[reference_type]:
            namespaces_list.append(reference_dic['namespace'])
    return namespaces_list


def _get_last_version_id(work_env_id):
    version_row = project.get_last_work_version(work_env_id, 'id')
    if not version_row:
        return None
    return version_row[0]


def _get_default_last_version_id(stage_id):
    stage_row = project.get_stage_data(stage_id)
    if not stage_row:
        return None
    default_variant_row = project.get_variant_data(
        stage_row.get('default_variant_id'))
    if not default_variant_row:
        return None
    default_work_env_row = project.get_work_env_data(
        default_variant_row.get('default_work_env_id'))
    if not default_work_env_row:
        return None
    return _get_last_version_id(default_work_env_row['id'])


def _stage_label(stage_id):
    """Return a readable 'asset/stage' label for log/progress messages."""
    stage_row = project.get_stage_data(stage_id)
    if not stage_row:
        return f"stage {stage_id}"
    asset_row = project.get_asset_data(stage_row['asset_id'])
    asset_name = asset_row['name'] if asset_row else '?'
    return f"{asset_name}/{stage_row['name']}"
