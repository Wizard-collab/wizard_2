from wizard.core import repository
from wizard.core import db_utils
users = repository.get_user_names_list()
repository.init_artefacts_stock()
for user in users:
	repository.modify_user_xp(user, 0)
	repository.modify_user_total_xp(user, 0)
	repository.modify_user_level(user, 0)
	repository.modify_user_life(user, 100)
	repository.modify_user_coins(user, 5000)
	repository.modify_user_artefacts(user, [])
	repository.modify_keeped_artefacts(user, dict())
	
	db_utils.update_data('repository',
                                'users',
                                ('comments_count', 0),
                                ('user_name', user))
	db_utils.update_data('repository',
                                'users',
                                ('work_time', 0),
                                ('user_name', user))