# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
import copy
import json
import logging
import os
import importlib
import traceback
import sys

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import tags_widget

# Wizard modules
from wizard.core import path_utils
from wizard.core import project
from wizard.core import environment
from wizard.core import repository
from wizard.core import batcher
from wizard.core import subtask
from wizard.vars import ressources

logger = logging.getLogger(__name__)

# Block categories, ordered filter -> argument -> process
FILTER = 'filter'
ARGUMENT = 'argument'
WIZARD_ACTION = 'wizard_action'
PROCESS = 'process'

_block_ranks = {FILTER: 0, ARGUMENT: 1, WIZARD_ACTION: 2, PROCESS: 3}

# Subtle, distinct backgrounds per block category (kept translucent so the
# dark theme still shows through).
_CATEGORY_BACKGROUNDS = {
    FILTER: 'rgba(74, 144, 217, 45)',        # blue
    ARGUMENT: 'rgba(232, 163, 61, 45)',      # orange
    WIZARD_ACTION: 'rgba(150, 112, 210, 45)',  # purple
    PROCESS: 'rgba(86, 183, 109, 45)',       # green
}

# Where opened/saved sequences are stored (inside the current project)
_module_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(os.path.dirname(_module_dir))


def get_sequences_dir():
    project_name = environment.get_project_name()
    if project_name:
        project_path = repository.get_project_path_by_name(project_name)
        if project_path:
            return os.path.join(project_path, 'batch_sequences')
    return os.path.join(_project_root, 'batch_sequences')


def category_rank(category):
    """Return the ordering rank of a block category
    (filter < argument < wizard_action < process)."""
    return _block_ranks.get(category, 3)


class batcher_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(batcher_widget, self).__init__(parent)

        self.sequences = []
        self.current_sequence = None
        self._suppress_save = False

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Batcher")

        self.build_ui()
        self.connect_functions()

        # Load the sequences saved in the project batch_sequences folder
        self.load_sequences()
        if not self.sequences:
            self.new_sequence(name="Default", blocks=[
                {'type': 'stage_selection', 'data': {}},
                {'type': 'comment', 'data': {}},
                {'type': 'update_all', 'data': {}},
                {'type': 'batch_export_data', 'data': {}},
                {'type': 'batch_video', 'data': {}},
                {'type': 'open_and_save', 'data': {}},
            ])
        else:
            self.set_current_sequence(0)

    def toggle(self):
        if self.isVisible():
            if not self.isActiveWindow():
                self.show()
                self.raise_()
                self.refresh()
            else:
                self.hide()
        else:
            self.show()
            self.raise_()
            self.refresh()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        # Toolbar / header
        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setObjectName('transparent_widget')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(8)
        self.header_widget.setLayout(self.header_layout)

        self.header_title_label = QtWidgets.QLabel("Batch sequences")
        self.header_title_label.setStyleSheet(
            "font-size: 18px; font-weight: bold;")
        self.header_layout.addWidget(self.header_title_label)
        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed))

        self.add_block_button = QtWidgets.QPushButton("＋ Add block")
        self.add_block_button.setObjectName('blue_button')
        self.header_layout.addWidget(self.add_block_button)

        self.new_sequence_button = QtWidgets.QPushButton("New")
        self.header_layout.addWidget(self.new_sequence_button)

        self.delete_sequence_button = QtWidgets.QPushButton("Delete")
        self.header_layout.addWidget(self.delete_sequence_button)

        self.header_widget.setFixedHeight(40)
        self.main_layout.addWidget(self.header_widget)

        # Splitter: sequence library (left) + blocks editor (right)
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)

        # --- Sequence library ---
        self.library_widget = QtWidgets.QWidget()
        self.library_widget.setObjectName('round_frame')
        self.library_layout = QtWidgets.QVBoxLayout()
        self.library_layout.setContentsMargins(8, 8, 8, 8)
        self.library_layout.setSpacing(6)
        self.library_widget.setLayout(self.library_layout)

        self.library_title_label = QtWidgets.QLabel("Sequences library")
        self.library_title_label.setStyleSheet("font-weight: bold;")
        self.library_layout.addWidget(self.library_title_label)

        self.library_list = QtWidgets.QListWidget()
        self.library_layout.addWidget(self.library_list)

        self.splitter.addWidget(self.library_widget)

        # --- Blocks editor ---
        self.blocks_scrollArea = QtWidgets.QScrollArea()
        self.blocks_scrollBar = self.blocks_scrollArea.verticalScrollBar()

        self.blocks_scrollArea_widget = QtWidgets.QWidget()
        self.blocks_scrollArea_widget.setObjectName('dark_widget')
        self.blocks_scrollArea_layout = QtWidgets.QVBoxLayout()
        self.blocks_scrollArea_layout.setSpacing(6)
        self.blocks_scrollArea_widget.setLayout(self.blocks_scrollArea_layout)

        self.blocks_scrollArea.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.blocks_scrollArea.setWidgetResizable(True)
        self.blocks_scrollArea.setWidget(self.blocks_scrollArea_widget)

        self.splitter.addWidget(self.blocks_scrollArea)
        self.splitter.setSizes([220, 600])

        self.main_layout.addWidget(self.splitter)

        # Execute button at the bottom
        self.execute_button = QtWidgets.QPushButton("Execute")
        self.execute_button.setObjectName('blue_button')
        self.execute_button.setMinimumHeight(36)
        self.main_layout.addWidget(self.execute_button)

    # ------------------------------------------------------------------
    # Sequence management
    # ------------------------------------------------------------------
    def new_sequence(self, name="Sequence", blocks=None):
        seq = {'name': name, 'blocks': blocks if blocks is not None else []}
        self.sequences.append(seq)
        self.refresh_library()
        self.set_current_sequence(len(self.sequences) - 1)

    def set_current_sequence(self, index):
        if 0 <= index < len(self.sequences):
            self.current_sequence = self.sequences[index]
            self.rebuild_blocks()

    def set_current_sequence_by_name(self, name):
        for i, seq in enumerate(self.sequences):
            if seq['name'] == name:
                self.set_current_sequence(i)
                return

    def load_sequences(self):
        sequences_dir = get_sequences_dir()
        if not os.path.isdir(sequences_dir):
            return
        for name in sorted(os.listdir(sequences_dir)):
            if not name.endswith('.json'):
                continue
            file_path = os.path.join(sequences_dir, name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load sequence {file_path}: {e}")
                continue
            seq_name = data.get('name') or os.path.splitext(name)[0]
            blocks = self._migrate_blocks(data.get('blocks', []))
            self.sequences.append(
                {'name': seq_name, 'blocks': blocks})
        self.refresh_library()

    def _migrate_blocks(self, blocks):
        """Convert old block types to the current ones on load."""
        migrated = []
        for block in blocks:
            block_type = block.get('type', '')
            if block_type == 'import_and_update_all':
                # Old block = import ALL + update ALL, now two separate blocks.
                migrated.append({'type': 'import_all', 'data': {}})
                migrated.append({'type': 'update_all', 'data': {}})
            else:
                migrated.append(block)
        return migrated

    @staticmethod
    def block_record(block_widget):
        return getattr(block_widget, '_record', None)

    # ------------------------------------------------------------------
    # Add / remove blocks
    # ------------------------------------------------------------------
    def add_block_from_library(self, type_name):
        if self.current_sequence is None:
            return
        self.current_sequence['blocks'].append(
            {'type': type_name, 'data': {}})
        self.rebuild_blocks()

    def remove_block(self, block_widget):
        if self.current_sequence is None:
            return
        record = self.block_record(block_widget)
        if record is not None and record in self.current_sequence['blocks']:
            self.current_sequence['blocks'].remove(record)
        self.rebuild_blocks()

    def move_block_in_sequence(self, block_widget, direction):
        if self.current_sequence is None:
            return
        blocks = self.current_sequence['blocks']
        record = self.block_record(block_widget)
        if record is None or record not in blocks:
            return
        index = blocks.index(record)
        new_index = index + direction
        if 0 <= new_index < len(blocks):
            blocks.pop(index)
            blocks.insert(new_index, record)
        self.rebuild_blocks()

    def show_block_info(self, block_widget):
        type_name = getattr(block_widget, 'type_name', '')
        title = getattr(block_widget, 'title', 'Block')
        inputs, outputs = batcher.get_block_io(type_name)
        text = f"{title}  ({type_name})\n\n"
        text += "Inputs (reads):\n"
        text += ('\n'.join(f"  • {i[0]}  ({i[1]})" for i in inputs)
                 or "  none") + "\n\n"
        text += "Outputs (writes):\n"
        text += ('\n'.join(f"  • {o[0]}  ({o[1]})" for o in outputs)
                 or "  none")
        QtWidgets.QMessageBox.information(self, title, text)

    def on_block_data_changed(self, block_widget):
        # During a rebuild the widgets are just being re-created from the
        # saved records; don't trigger a save for each one. A single save
        # happens once the rebuild is done.
        if self._suppress_save:
            return
        record = self.block_record(block_widget)
        if record is not None:
            record['data'] = block_widget.get_data()
        self.save_current_sequence()

    def show_library_menu(self):
        menu = gui_utils.QMenu(self)
        grouped = {}
        for cat, label, type_name in get_block_library():
            grouped.setdefault(cat, []).append((label, type_name))
        first = True
        for cat in [FILTER, ARGUMENT, WIZARD_ACTION, PROCESS]:
            if cat not in grouped:
                continue
            if not first:
                menu.addSeparator()
            first = False
            for label, type_name in grouped[cat]:
                action = menu.addAction(label)
                action.type_name = type_name
        action = menu.exec(QtGui.QCursor().pos())
        if action is not None and hasattr(action, 'type_name'):
            self.add_block_from_library(action.type_name)

    # ------------------------------------------------------------------
    # Build the UI from the current sequence
    # ------------------------------------------------------------------
    def rebuild_blocks(self):
        layout = self.blocks_scrollArea_layout

        # Clear everything
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)

        # Trailing spacer
        layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding))

        if self.current_sequence is None:
            return

        # Rebuild the widgets without firing a save per block (set_data
        # emits data_changed). A single save persists the auto-assigned IO.
        self._suppress_save = True
        try:
            blocks = self.current_sequence['blocks']
            # Deterministically assign typed output variable names + default
            # input bindings, and persist them in each block's data.
            assignments = batcher.auto_assign_variables(blocks)

            for i, record in enumerate(blocks):
                block = instantiate_block(record.get('type', ''))
                if block is None:
                    continue
                block._record = record
                block.remove_signal.connect(self.remove_block)
                block.data_changed.connect(
                    lambda b=block: self.on_block_data_changed(b))
                block.move_up.connect(
                    lambda b=block: self.move_block_in_sequence(b, -1))
                block.move_down.connect(
                    lambda b=block: self.move_block_in_sequence(b, 1))
                block.info_requested.connect(self.show_block_info)
                assignment = assignments[i] if i < len(assignments) else None
                if assignment:
                    block.setup_io(assignment['available'],
                                   assignment['inputs'],
                                   assignment['outputs'])
                block.set_data(record.get('data', {}))
                self.add_block_widget(block)

            self.build_sequence_layout()
        finally:
            self._suppress_save = False

        # Persist the auto-assigned variable IO exactly once per rebuild.
        self.save_current_sequence()

    def add_block_widget(self, widget):
        # Append at the end (manual order) - just above the trailing spacer.
        index = self.blocks_scrollArea_layout.count() - 1
        self.blocks_scrollArea_layout.insertWidget(index, widget)
        return widget

    def build_sequence_layout(self):
        # Manual order: just number the blocks in display order.
        layout = self.blocks_scrollArea_layout
        n = 0
        for i in range(layout.count()):
            item = layout.itemAt(i)
            w = item.widget() if item else None
            if isinstance(w, blockWidget):
                n += 1
                w.set_number(n)

    # ------------------------------------------------------------------
    # Serialization (save / open)
    # ------------------------------------------------------------------
    def collect_live_blocks(self):
        """Return the live block widgets currently displayed, in order."""
        widgets = []
        layout = self.blocks_scrollArea_layout
        for i in range(layout.count()):
            item = layout.itemAt(i)
            w = item.widget() if item else None
            if isinstance(w, blockWidget):
                widgets.append(w)
        return widgets

    def sequence_to_dict(self):
        # Build from the sequence RECORDS (complete list whose data is kept
        # fresh by live updates). This can NEVER read a half-built layout
        # during a rebuild, so blocks don't disappear when saving.
        if self.current_sequence is None:
            return {'name': '', 'blocks': []}
        blocks = []
        for record in self.current_sequence['blocks']:
            blocks.append({
                'type': record.get('type', ''),
                'data': record.get('data', {}) or {},
            })
        return {'name': self.current_sequence['name'], 'blocks': blocks}

    def save_current_sequence(self):
        """Save the current sequence to disk."""
        if self.current_sequence is None:
            return
        sequences_dir = get_sequences_dir()
        os.makedirs(sequences_dir, exist_ok=True)
        file_path = os.path.join(
            sequences_dir, f"{self.current_sequence['name']}.json")
        seq = self.sequence_to_dict()
        logger.info(f"Auto-saving '{seq['name']}' blocks: "
                    f"{[b.get('type') for b in seq['blocks']]}")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(seq, f, indent=2, ensure_ascii=False)
            logger.info(f"Auto-saved sequence to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save sequence: {e}")

    def read_sequence_data(self, sequence_name):
        """Return the sequence dict read from disk (source of truth), or None."""
        file_path = os.path.join(
            get_sequences_dir(), f"{sequence_name}.json")
        if not os.path.isfile(file_path):
            logger.info(f"No sequence file at {file_path}")
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Read sequence from {file_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to read sequence {file_path}: {e}")
            return None

    def play_sequence(self, name):
        """Switch to the named sequence and execute its SAVED (disk) version."""
        logger.info(f"play_sequence: name={name}")
        self.set_current_sequence_by_name(name)
        data = self.read_sequence_data(name)
        if data is not None:
            self.execute_sequence_data(data)

    def on_new_sequence(self):
        name, ok = QtWidgets.QInputDialog.getText(
            self, "New sequence", "Sequence name:")
        if ok and name:
            self.new_sequence(name=name, blocks=[])

    def on_delete_sequence(self):
        if not self.sequences or self.current_sequence is None:
            return
        index = self.sequences.index(self.current_sequence)
        seq_name = self.current_sequence['name']
        self.sequences.pop(index)
        # Remove the persisted file too
        file_path = os.path.join(get_sequences_dir(), f"{seq_name}.json")
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Failed to delete sequence file: {e}")
        self.refresh_library()
        if not self.sequences:
            self.new_sequence(name="Default", blocks=[])
        else:
            self.set_current_sequence(min(index, len(self.sequences) - 1))

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------
    def execute_sequence(self):
        if self.current_sequence is None:
            return
        logger.info(f"execute_sequence: current name={self.current_sequence['name']}")
        data = self.read_sequence_data(self.current_sequence['name'])
        if data is not None:
            self.execute_sequence_data(data)

    def execute_sequence_data(self, data):
        # Log exactly which blocks are being launched (useful to spot a
        # block present in the in-memory sequence unexpectedly).
        block_types = [b.get('type', '?') for b in data.get('blocks', [])]
        logger.info(f"Launching sequence '{data.get('name', '')}' with "
                    f"blocks: {block_types}")
        # Launch the execution as a background subtask (subprocess with the
        # wizard environment), so the UI stays responsive.
        command = "from wizard.core import batcher\n"
        command += f"batcher.execute_sequence({repr(data)})\n"
        task = subtask.subtask(pycmd=command, print_stdout=False)
        task.start()

    # ------------------------------------------------------------------
    # Sequence library
    # ------------------------------------------------------------------
    def refresh_library(self):
        self.library_list.clear()
        for index in range(len(self.sequences)):
            self.add_library_sequence(index)

    def add_library_sequence(self, index):
        sequence = self.sequences[index]
        item = QtWidgets.QListWidgetItem()
        item.setText('')
        item.setSizeHint(QtCore.QSize(0, 30))
        # Bind to the sequence NAME, which is stable across list changes.
        item.setData(QtCore.Qt.ItemDataRole.UserRole, sequence['name'])
        self.library_list.addItem(item)

        row = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout()
        row_layout.setContentsMargins(8, 0, 8, 0)
        row_layout.setSpacing(6)
        row.setLayout(row_layout)

        name_label = QtWidgets.QLabel(sequence['name'])
        row_layout.addWidget(name_label)
        row_layout.addStretch()

        play_button = gui_utils.transparent_button(
            ressources._player_play_icon_, ressources._player_play_icon_hover_)
        play_button.setFixedSize(24, 24)
        play_button.setIconSize(QtCore.QSize(16, 16))
        play_button.setToolTip("Execute this sequence")
        play_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        # Note: QPushButton 'clicked' passes a 'checked' bool; swallow it via
        # the leading default so it doesn't overwrite the sequence name.
        play_button.clicked.connect(
            lambda _checked=False, name=sequence['name']: self.play_sequence(name))
        row_layout.addWidget(play_button)

        self.library_list.setItemWidget(item, row)

    def on_library_item_clicked(self, item):
        name = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if name:
            self.set_current_sequence_by_name(name)

    # ------------------------------------------------------------------
    # Connections
    # ------------------------------------------------------------------
    def connect_functions(self):
        self.execute_button.clicked.connect(self.execute_sequence)
        self.add_block_button.clicked.connect(self.show_library_menu)
        self.new_sequence_button.clicked.connect(self.on_new_sequence)
        self.delete_sequence_button.clicked.connect(self.on_delete_sequence)
        self.library_list.itemClicked.connect(self.on_library_item_clicked)

    def refresh(self):
        pass


class blockWidget(QtWidgets.QFrame):
    category = PROCESS
    icon = ''

    remove_signal = pyqtSignal(object)
    data_changed = pyqtSignal()
    move_up = pyqtSignal(object)
    move_down = pyqtSignal(object)
    info_requested = pyqtSignal(object)

    def __init__(self, title, parent=None):
        super(blockWidget, self).__init__(parent)
        self.title = title
        self._record = None

        self.setObjectName('round_frame')
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(8)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.setLayout(self.main_layout)

        # Distinct, subtle background color by block category
        bg_color = _CATEGORY_BACKGROUNDS.get(
            self.category, 'rgba(75, 75, 87, 45)')
        self.setStyleSheet(f"#round_frame{{background-color: {bg_color};}}")

        # Title for the block (number + icon + text + remove)
        self.title_widget = QtWidgets.QWidget()
        self.title_widget.setObjectName('transparent_widget')
        self.title_layout = QtWidgets.QHBoxLayout()
        self.title_layout.setContentsMargins(0, 0, 0, 0)
        self.title_layout.setSpacing(6)
        self.title_widget.setLayout(self.title_layout)

        self.number_label = QtWidgets.QLabel()
        self.number_label.setStyleSheet("font-weight: bold; color: gray;")
        self.number_label.setFixedWidth(22)
        self.title_layout.addWidget(self.number_label)

        self.title_icon_label = QtWidgets.QLabel()
        self.title_icon_label.setFixedSize(16, 16)
        if self.icon:
            self.title_icon_label.setPixmap(QtGui.QIcon(self.icon).pixmap(16))
        self.title_layout.addWidget(self.title_icon_label)

        self.title_label = QtWidgets.QLabel(self.title)
        self.title_label.setStyleSheet("font-weight: bold;")
        self.title_label.setFixedHeight(18)
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch()

        self.info_button = QtWidgets.QPushButton()
        self.info_button.setFixedSize(16, 16)
        self.info_button.setIcon(QtGui.QIcon(ressources._info_icon_))
        self.info_button.setIconSize(QtCore.QSize(12, 12))
        self.info_button.setToolTip("Show accepted inputs and outputs")
        self.info_button.clicked.connect(
            lambda: self.info_requested.emit(self))
        self.title_layout.addWidget(self.info_button)

        self.up_button = QtWidgets.QPushButton()
        self.up_button.setFixedSize(16, 16)
        self.up_button.setIcon(QtGui.QIcon(ressources._up_arrow_))
        self.up_button.setIconSize(QtCore.QSize(12, 12))
        self.up_button.setToolTip("Move up")
        self.up_button.clicked.connect(
            lambda: self.move_up.emit(self))
        self.title_layout.addWidget(self.up_button)

        self.down_button = QtWidgets.QPushButton()
        self.down_button.setFixedSize(16, 16)
        self.down_button.setIcon(QtGui.QIcon(ressources._down_arrow_))
        self.down_button.setIconSize(QtCore.QSize(12, 12))
        self.down_button.setToolTip("Move down")
        self.down_button.clicked.connect(
            lambda: self.move_down.emit(self))
        self.title_layout.addWidget(self.down_button)

        self.remove_button = gui_utils.close_button()
        self.remove_button.setFixedSize(16, 16)
        self.remove_button.setIconSize(QtCore.QSize(12, 12))
        self.remove_button.setToolTip("Remove this block")
        self.remove_button.clicked.connect(
            lambda: self.remove_signal.emit(self))
        self.title_layout.addWidget(self.remove_button)

        self.main_layout.addWidget(self.title_widget)

        # Placeholder for block content
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_layout.setSpacing(8)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.content_layout)

        # Typed IO section: upstream variable selectors + produced variables.
        self.io_section = QtWidgets.QWidget()
        self.io_section.setObjectName('transparent_widget')
        self.io_layout = QtWidgets.QVBoxLayout()
        self.io_layout.setContentsMargins(0, 0, 0, 0)
        self.io_layout.setSpacing(4)
        self.io_section.setLayout(self.io_layout)
        self.main_layout.addWidget(self.io_section)

        self._input_combos = {}
        self._io_available = []
        self._io_inputs = {}
        self._io_outputs = {}

    # ------------------------------------------------------------------
    # Typed variable IO (set by the parent after auto-assignment)
    # ------------------------------------------------------------------
    def setup_io(self, available, inputs, outputs):
        """Populate the variable selectors and produced-variable labels.

        ``available`` are upstream variables (name/type pairs) visible to this
        block, ``inputs`` the current input bindings and ``outputs`` the
        auto-assigned output variable names.
        """
        self._io_available = [list(p) for p in (available or [])]
        self._io_inputs = dict(inputs or {})
        self._io_outputs = dict(outputs or {})

        # Clear any previously built rows.
        while self.io_layout.count():
            item = self.io_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
        self._input_combos = {}

        inputs_sig, outputs_sig = batcher.get_block_io(self.type_name)
        pending_combos = []

        for in_name, in_type in inputs_sig:
            if in_type == batcher.TYPE_ANY:
                continue
            row = QtWidgets.QWidget()
            # Plain QWidgets get the global #2c2c33 background; force
            # transparent so the block's category color shows through the
            # label and the combo.
            row.setObjectName('transparent_widget')
            row_l = QtWidgets.QHBoxLayout()
            row_l.setContentsMargins(0, 0, 0, 0)
            row_l.setSpacing(6)

            labels = getattr(self, 'input_labels', {})
            label_text = labels.get(in_name, in_name)
            lab = QtWidgets.QLabel(label_text)
            lab.setObjectName('gray_label')
            row_l.addWidget(lab)

            combo = QtWidgets.QComboBox()
            combo.addItem("— none —", None)
            for var_name, vtype in self._io_available:
                if vtype == in_type:
                    combo.addItem(var_name, var_name)
            current = self._io_inputs.get(in_name)
            idx = combo.findData(current)
            if idx < 0:
                idx = 0
            combo.setCurrentIndex(idx)
            pending_combos.append((in_name, combo))

            row_l.addWidget(combo, 1)
            row.setLayout(row_l)
            self.io_layout.addWidget(row)

        # Connect combo changes only after everything is built, so the
        # initial population does not trigger spurious saves.
        for name, combo in pending_combos:
            combo.currentIndexChanged.connect(self._on_io_input_changed)
            self._input_combos[name] = combo

        if outputs_sig:
            out_parts = []
            for out_name, out_type in outputs_sig:
                if out_type == batcher.TYPE_ANY:
                    continue
                out_parts.append(f"{out_name}: {self._io_outputs.get(out_name, '')}")
            if out_parts:
                out_label = QtWidgets.QLabel("→ " + ",  ".join(out_parts))
                out_label.setObjectName('gray_label')
                self.io_layout.addWidget(out_label)

    def _on_io_input_changed(self, index=0):
        for name, combo in self._input_combos.items():
            self._io_inputs[name] = combo.currentData()
        self.data_changed.emit()

    def _io_data(self):
        """Return the serialized input/output variable bindings."""
        return {'inputs': dict(self._io_inputs),
                'outputs': dict(self._io_outputs)}

    def _merge_io(self, payload):
        payload['inputs'] = dict(self._io_inputs)
        payload['outputs'] = dict(self._io_outputs)
        return payload

    def set_number(self, number):
        self.number_label.setText(f"{number}.")

    def connect_functions(self):
        pass

    def get_data(self):
        """Return the serialized data of this block."""
        return self._io_data()

    def set_data(self, data):
        """Restore the block state from serialized data."""
        return self


class comment_blockWidget(blockWidget):
    type_name = 'comment'
    category = ARGUMENT
    icon = ressources._tool_comment_

    def __init__(self, parent=None):
        super(comment_blockWidget, self).__init__("Comment", parent)

    def build_ui(self):
        super(comment_blockWidget, self).build_ui()
        self.comment_field = gui_utils.no_return_textEdit()
        self.comment_field.setPlaceholderText("Your comment")
        self.comment_field.setFixedHeight(48)
        self.comment_field.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed)
        self.content_layout.addWidget(self.comment_field)

    def connect_functions(self):
        self.comment_field.textChanged.connect(self.propose_tags)
        self.comment_field.textChanged.connect(self.data_changed.emit)

    def propose_tags(self):
        text = self.comment_field.toPlainText()
        position_rect = self.comment_field.cursorRect()
        pos = self.comment_field.mapToGlobal(
            QtCore.QPoint(position_rect.x()+20, position_rect.y()))
        self.tags_widget = tags_widget.tags_widget(pos=pos, text=text)
        self.tags_widget.other_key_pressed.connect(
            self.comment_field.keyPressEvent)
        self.tags_widget.returned_text.connect(self.comment_field.setText)
        self.tags_widget.returned_text.connect(self.move_cursor_to_end)
        self.tags_widget.execute()

    def move_cursor_to_end(self):
        self.comment_field.moveCursor(QtGui.QTextCursor.MoveOperation.End)

    def get_data(self):
        return self._merge_io({'comment': self.comment_field.toPlainText()})

    def set_data(self, data):
        if data:
            self.comment_field.setText(data.get('comment', ''))
        return self


class refresh_assets_blockWidget(blockWidget):
    def __init__(self, title, parent=None):
        super(refresh_assets_blockWidget, self).__init__(title, parent)


class batch_export_data_blockWidget(refresh_assets_blockWidget):
    type_name = 'batch_export_data'
    icon = ressources._exports_icon_

    def __init__(self, parent=None):
        super(batch_export_data_blockWidget, self).__init__("Batch export data", parent)


class batch_video_blockWidget(refresh_assets_blockWidget):
    type_name = 'batch_video'
    icon = ressources._tool_video_

    def __init__(self, parent=None):
        super(batch_video_blockWidget, self).__init__("Batch video", parent)


class import_all_blockWidget(blockWidget):
    type_name = 'import_all'
    category = ARGUMENT
    icon = ressources._tool_update_

    def __init__(self, parent=None):
        super(import_all_blockWidget, self).__init__("Import all", parent)


class update_all_blockWidget(blockWidget):
    type_name = 'update_all'
    category = ARGUMENT
    icon = ressources._tool_update_

    def __init__(self, parent=None):
        super(update_all_blockWidget, self).__init__("Update all", parent)


class open_and_save_blockWidget(blockWidget):
    type_name = 'open_and_save'
    icon = ressources._save_icon_

    def __init__(self, parent=None):
        super(open_and_save_blockWidget, self).__init__("Open and save", parent)


class create_reference_blockWidget(blockWidget):
    type_name = 'create_reference'
    category = WIZARD_ACTION
    icon = ressources._references_icon_
    # Friendlier labels for the typed inputs (shown instead of the raw var
    # name next to each selector).
    input_labels = {
        'reference_selection': 'Stages to reference:',
        'stages': 'Create references into:',
    }

    def __init__(self, parent=None):
        super(create_reference_blockWidget, self).__init__(
            "Create reference", parent)

    def build_ui(self):
        super(create_reference_blockWidget, self).build_ui()
        description = QtWidgets.QLabel(
            "Creates a reference to the exports of the selected stages, "
            "inside the target stages' work environment.")
        description.setWordWrap(True)
        description.setStyleSheet("color: gray;")
        self.content_layout.addWidget(description)

    def get_data(self):
        return self._merge_io({})


class category_selection_blockWidget(blockWidget):
    type_name = 'category_selection'
    category = FILTER
    icon = ressources._folder_icon_

    def __init__(self, parent=None):
        self._categories = project.get_all_categories() or []
        super(category_selection_blockWidget, self).__init__(
            "Category selection", parent)

    def build_ui(self):
        super(category_selection_blockWidget, self).build_ui()
        self.category_combo = QtWidgets.QComboBox()
        for category_row in self._categories:
            self.category_combo.addItem(category_row['name'],
                                        category_row['id'])
        self.content_layout.addWidget(self.category_combo)

    def connect_functions(self):
        self.category_combo.currentIndexChanged.connect(
            self.data_changed.emit)

    def get_data(self):
        return self._merge_io({'category': self.category_combo.currentData()})

    def set_data(self, data):
        if data:
            index = self.category_combo.findData(data.get('category'))
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        return self


class domain_selection_blockWidget(blockWidget):
    type_name = 'domain_selection'
    category = FILTER
    icon = ressources._assets_group_icon_

    def __init__(self, parent=None):
        self._domains = project.get_domains() or []
        super(domain_selection_blockWidget, self).__init__(
            "Domain selection", parent)

    def build_ui(self):
        super(domain_selection_blockWidget, self).build_ui()
        self.domain_combo = QtWidgets.QComboBox()
        for domain_row in self._domains:
            self.domain_combo.addItem(domain_row['name'], domain_row['id'])
        self.content_layout.addWidget(self.domain_combo)

    def connect_functions(self):
        self.domain_combo.currentIndexChanged.connect(
            self.data_changed.emit)

    def get_data(self):
        return self._merge_io({'domain': self.domain_combo.currentData()})

    def set_data(self, data):
        if data:
            index = self.domain_combo.findData(data.get('domain'))
            if index >= 0:
                self.domain_combo.setCurrentIndex(index)
        return self


class assembly_blockWidget(blockWidget):
    type_name = 'assembly'
    category = WIZARD_ACTION
    icon = ressources._references_icon_

    def __init__(self, parent=None):
        super(assembly_blockWidget, self).__init__(
            "Assembly", parent)


class code_blockWidget(blockWidget):
    type_name = 'code'
    category = WIZARD_ACTION
    icon = ressources._python_icon_

    def __init__(self, parent=None):
        super(code_blockWidget, self).__init__("Code", parent)

    def build_ui(self):
        super(code_blockWidget, self).build_ui()
        self.code_field = QtWidgets.QPlainTextEdit()
        self.code_field.setPlaceholderText(
            "# Python code using the wizard API (wapi)\n"
            "# e.g.\n"
            "# wapi.project.get_all_stages()")
        self.code_field.setMinimumHeight(120)
        self.content_layout.addWidget(self.code_field)

    def connect_functions(self):
        self.code_field.textChanged.connect(self.data_changed.emit)

    def get_data(self):
        return self._merge_io({'code': self.code_field.toPlainText()})

    def set_data(self, data):
        if data:
            code = data.get('code', '')
            if code:
                self.code_field.setPlainText(code)
        return self


class stage_selection_blockWidget(blockWidget):
    type_name = 'stage_selection'
    category = FILTER
    icon = ressources._filter_icon_

    def __init__(self, parent=None):
        # Populate lookups BEFORE build_ui() runs (build_ui calls refresh_search)
        self._asset_names = dict()
        self._asset_categories = dict()
        self._category_names = dict()
        for asset_row in project.get_all_assets():
            self._asset_names[asset_row['id']] = asset_row['name']
            self._asset_categories[asset_row['id']] = asset_row['category_id']
        for category_row in project.get_all_categories():
            self._category_names[category_row['id']] = category_row['name']
        super(stage_selection_blockWidget, self).__init__("Stage selection", parent)

    def build_ui(self):
        super(stage_selection_blockWidget, self).build_ui()

        self.stage_filter_edit = QtWidgets.QLineEdit()
        self.stage_filter_edit.setPlaceholderText(
            "Filter stages, e.g. characters & Lola")
        self.stage_filter_edit.setFixedHeight(24)
        self.content_layout.addWidget(self.stage_filter_edit)

        self.stages_label = QtWidgets.QLabel("Affected stages")
        self.stages_label.setObjectName('gray_label')
        self.content_layout.addWidget(self.stages_label)

        # Read-only, non-interactive display (no hover/selection)
        self.stages_textedit = QtWidgets.QPlainTextEdit()
        self.stages_textedit.setReadOnly(True)
        self.stages_textedit.setLineWrapMode(
            QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
        self.stages_textedit.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.NoTextInteraction)
        self.stages_textedit.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.content_layout.addWidget(self.stages_textedit)

        self.refresh_search()

    def connect_functions(self):
        self.stage_filter_edit.textChanged.connect(self.refresh_search)
        self.stage_filter_edit.textChanged.connect(self.data_changed.emit)

    def refresh_search(self):
        self.stages_textedit.clear()
        query = self.stage_filter_edit.text()
        all_stages = project.get_all_stages()
        keywords_sets = query.split('+')
        for keywords_set in keywords_sets:
            keywords = keywords_set.split('&')
            for stage_row in all_stages:
                stage_row_cp = copy.deepcopy(stage_row)
                for key in ('id', 'creation_time', 'creation_user',
                            'work_time', 'progress', 'estimated_time',
                            'default_variant_id', 'asset_id', 'domain_id'):
                    stage_row_cp.pop(key, None)
                values = list(stage_row_cp.values())
                data_list = [str(data_block) for data_block in values]
                data = (' ').join(data_list)
                if all(keyword.upper() in data.upper()
                       for keyword in keywords):
                    asset_name = self._asset_names.get(
                        stage_row['asset_id'], '?')
                    category_id = self._asset_categories.get(
                        stage_row['asset_id'])
                    category_name = self._category_names.get(
                        category_id, '?')
                    display = (f"{category_name}/{asset_name}/"
                               f"{stage_row['name']}")
                    self.stages_textedit.appendPlainText(display)

    def get_data(self):
        return self._merge_io({'filter': self.stage_filter_edit.text()})

    def set_data(self, data):
        if data:
            filter_text = data.get('filter', '')
            if filter_text:
                self.stage_filter_edit.setText(filter_text)
        return self


# ------------------------------------------------------------------
# Block library
# ------------------------------------------------------------------
def get_block_library():
    """Return (category, label, type_name) for every available block."""
    return [
        (FILTER, 'Stage selection', 'stage_selection'),
        (FILTER, 'Category selection', 'category_selection'),
        (FILTER, 'Domain selection', 'domain_selection'),
        (ARGUMENT, 'Comment', 'comment'),
        (ARGUMENT, 'Import all', 'import_all'),
        (ARGUMENT, 'Update all', 'update_all'),
        (PROCESS, 'Batch export data', 'batch_export_data'),
        (PROCESS, 'Batch video', 'batch_video'),
        (PROCESS, 'Open and save', 'open_and_save'),
        (WIZARD_ACTION, 'Create reference', 'create_reference'),
        (WIZARD_ACTION, 'Assembly', 'assembly'),
        (WIZARD_ACTION, 'Code', 'code'),
    ]


_block_class_map = {
    'stage_selection': stage_selection_blockWidget,
    'category_selection': category_selection_blockWidget,
    'domain_selection': domain_selection_blockWidget,
    'comment': comment_blockWidget,
    'import_all': import_all_blockWidget,
    'update_all': update_all_blockWidget,
    'batch_export_data': batch_export_data_blockWidget,
    'batch_video': batch_video_blockWidget,
    'open_and_save': open_and_save_blockWidget,
    'create_reference': create_reference_blockWidget,
    'assembly': assembly_blockWidget,
    'code': code_blockWidget,
}


def instantiate_block(type_name):
    cls = _block_class_map.get(type_name)
    if cls is None:
        return None
    return cls()
