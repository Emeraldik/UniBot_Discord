language = {}

LANG = 'ru'

language['en'] = {
    "precense_servers": {
	    '0' : "servers",
	    '1' : "servers",
	    '2' : "servers",
	    '3' : "servers",
	    '4' : "servers",
	    '5' : "servers",
	    '6' : "servers",
	    '7' : "servers",
	    '8' : "servers",
	    '9' : "servers",
	},
    "precense_users": "users",
    "game_price": "Game price",
    "discount_ended": "Promotion ended",
    "not_ru_akk": "(Not for RU account)",
    "game_link": "Distribution link",
    "discount_will_ended": "Promotion ends",
    "no_channel": "Channel not installed",
    "no_role": "Role not set",
    "no_message_changes": "Without changes",
    "message_changes_delete": "Messages will be deleted",
    "message_changes_edit": "Messages will change",
    "bot_started": "Bot launched",
    "bot_stoped": "Bot stopped",
    "settings": "Settings bot",
    "current_channel": "Distribution channel",
    "current_role": "Distribution Role",
    "current_mode": "Message Mode",
    "bot_status": "Status bot",
    "reset_submit_modal": "To reset the bot, enter 'SUBMIT'",
    "reset_submit": "Reset bot settings",
    "reset_canceled": "Error: bot settings reset canceled!",
    "reset_successful": "Reset completed successfully!",
    "reset_confirm": "Confirm",
    "return_to_settings": "Back to settings menu",
    "choose_channel": "Select text channel",
    "settings_channel": "Channel settings",
    "channel": "communities",
    "current_channel_for": "Current distribution channel for",
    "channel_not_exists": "Error: This channel no longer exists.",
    "last_channel": "last channel",
    "none_role": "No selected role",
    "choose_role": "Choose a role to mention",
    "settings_role": "Role settings",
    "current_role_for": "Current role for mention",
    "role_not_exists": "Error: This role no longer exists",
    "last_role": "Last Role",
    "delete_message": "Delete message",
    "edit_message": "Edit message",
    "none_message": "Do nothing with the message",
    "choose_message": "Select the mode",
    "settings_message": "Mode settings, what will happen to the message after the end of the promotion",
    "current_message_for": "Current mode",
    "last_message": "Last Mode",
    "bot_start": "Run a bot",
    "bot_stop": "Stop the bot",
    "channel_setup": "Select channel",
    "no_channels_guild": "There are no available text channels in this community",
    "message_setup": "Select a mode for messages",
    "role_setup": "Choose role",
    "no_roles_guild": "No roles available in this community",
    "reset": "Reset settings",
    "message_reset": "Are you sure you want to reset ALL bot settings in this community?",
    "fix_message_editor": "Edit message",
    "fix_message_editor_error": "Error: the key is not recognized, perhaps in the 'key' column you have written something other than ru or not_ru",
    "fix_message_apply": "Confirm Changes",
    "fix_message_edit_successful": "Change message : Success!",
    "fix_message_discard": "cancel changes",
    "fix_message_edit_discard": "Message Edit: Canceled!",
    "fix_message_how_view": "What the modified message will look like",
    "fix_message_delete_modal": "To delete a message type 'SUBMIT'",
    "fix_message_delete_submit": "Confirm deletion",
    "fix_message_delete_error": "Error: Post deletion canceled!",
    "fix_message_delete_successful": "Message deleted!",
    "fix_message_choose": "Choose a message",
    "fix_message_message_not_exists": "Error: This message no longer exists!",
    "fix_message_change_message": "Edit message",
    "fix_message_modal_title": "Name of the game",
    "fix_message_modal_description": "Game description",
    "fix_message_modal_url": "Link to the game in the Epic Games Store",
    "fix_message_modal_price": "Price per game",
    "fix_message_modal_key": "Distribution access in Russia, 'ru' or 'not_ru'",
    "fix_message_button_delete": "Delete message",
    "fix_message_how_view_now": "What does the message look like now?",
    "fix_message_no_messages": "There are no messages to edit/delete",
    "send_to_channel_choose": "Select the channel where to transfer the user with the nickname",
    "send_to_channel_sorry": "Sorry",
    "send_to_channel_no_voice": "must be in the voice channel",
    "send_to_channel_will_be_sent": "will be transferred to",
    "send_to_channel_channel": "channel",
    "send_to_channel_check_all": "View all voice channels",
    "give_permissions_describe": "True - grant permissions to control the bot, False - take them away",
    "give_permissions_all_ready": "All is ready",
    "give_permissions_new_status": "Gets a new status",
    "give_permissions_error_bot": "Error : Cannot give or take away bot powers to use UniBot",
    "dont_have_permissions": "You do not have sufficient permissions to use this command",
    "something_went_wrong": "Oops... An error has occurred! If you have the opportunity, write to the developer, preferably describe the circumstances under which the error occurred.",
    'bot_latency' : 'Bot latency',
   	'help_title' : 'Command help menu',
	'help_footer' : 'Commands available to users | All commands work within communities',
	'help_commands' : {
		'settings' : {
			'name' : 'uni_settings',
			'description' : '(Command is available to users with the \'Manage channels\' permission)\nBot settings for the community from which the command was called.',
		},
		'fix_message' : {
			'name' : 'uni_fix_message',
			'description' : '(Command is available to users with the \'Manage channels\' permission)\nManage messages, with distributions that are still active. You can change the name / description / price / region of distribution / link to the game, as well as delete the message through the bot.',
		},
		'ping' : {
			'name' : 'uni_ping',
			'description' : 'You can find out the current latency of the bot.',
		}
	},
	'admin_settings' : 'Administration Settings',
	'admin_settings_embed_title' : 'Selecting roles / users to access UniBot',
	'admin_settings_choose_role' : 'Select Roles',
	'admin_settings_choose_user' : 'Select Users',
	'admin_settings_embed_roles' : 'Roles',
	'admin_settings_embed_users' : 'Users'
}

language['ru'] = {
	"precense_servers": {
	    '0' : "серверов",
	    '1' : "сервер",
	    '2' : "сервера",
	    '3' : "сервера",
	    '4' : "сервера",
	    '5' : "серверов",
	    '6' : "серверов",
	    '7' : "серверов",
	    '8' : "серверов",
	    '9' : "серверов",
	},
	'precense_users' : 'чел',
	'game_price' : 'Цена игры',
	'discount_ended' : 'Акция закончилась',
	'not_ru_akk' : '(Не для RU аккаунта)',
	'game_link' : 'Ссылка на раздачу',
	'discount_will_ended' : 'Акция заканчивается',
	'no_channel' : 'Канал не установлен',
	'no_role' : 'Роль не установлена',
	'no_message_changes' : 'Без изменений',
	'message_changes_delete' : 'Сообщения будут удаляться',
	'message_changes_edit' : 'Сообщения будут изменяться',
	'bot_started' : 'Бот запущен',
	'bot_stoped' : 'Бот остановлен',
	'settings' : 'Настройки бота',
	'current_channel' : 'Канал для раздач',
	'current_role' : 'Роль для раздач',
	'current_mode' : 'Режим для сообщений',
	'bot_status' : 'Статус бота',
	'reset_submit_modal' : 'Для сброса настроек бота введите \'SUBMIT\'',
	'reset_submit' : 'Сброс настроек бота',
	'reset_canceled' : 'Ошибка : сброс настроек бота отменён!',
	'reset_successful' : 'Сброс настроек успешно произведён!',
	'reset_confirm' : 'Подтвердить',
	'return_to_settings' : 'Вернуться в меню настроек',
	'choose_channel' : 'Выберите текстовый канал',
	'settings_channel' : 'Настройки канала',
	'channel' : 'сообщества',
	'current_channel_for' : 'Текущий канал раздач для',
	'channel_not_exists' : 'Ошибка : такой канал больше не существует.',
	'last_channel' : 'Первоначальный канал',
	'none_role' : 'Нет выбранной роли',
	'choose_role' : 'Выберите роль для упоминания',
	'settings_role' : 'Настройки роли',
	'current_role_for' : 'Текущая роль для упоминания',
	'role_not_exists' : 'Ошибка : такой роли больше не существует',
	'last_role' : 'Первоначальная роль',
	'delete_message' : 'Удалить сообщение',
	'edit_message' : 'Изменить сообщение',
	'none_message' : 'Ничего не делать с сообщением',
	'choose_message' : 'Выберите режим',
	'settings_message' : 'Настройки режима, что произойдёт с сообщением, после окончания акции',
	'current_message_for' : 'Текущий режим',
	'last_message' : 'Прошлый режим',
	'bot_start' : 'Запустить бота',
	'bot_stop' : 'Остановить бота',
	'channel_setup' : 'Выбрать канал',
	'no_channels_guild' : 'Нет доступных текстовых каналов в этом сообществе',
	'message_setup' : 'Выбрать режим, для сообщений',
	'role_setup' : 'Выбрать роль',
	'no_roles_guild' : 'Нет доступных ролей в этом сообществе',
	'reset' : 'Сбросить настройки',
	'message_reset' : 'Вы точно уверены, что хотите сбросить ВСЕ настройки бота в этом сообществе?',
	'fix_message_editor' : 'Изменение сообщения',
	'fix_message_editor_error' : 'Ошибка : ключ не распознан, возможно в графе \'key\' вы прописали что-то иное, а не ru или not_ru',
	'fix_message_apply' : 'Подтвердить изменения',
	'fix_message_edit_successful' : 'Изменение сообщения : успешно!',
	'fix_message_discard' : 'Отменить изменения',
	'fix_message_edit_discard' : 'Изменение сообщения : отменено!',
	'fix_message_how_view' : 'Как будет выглядеть изменённое сообщение',
	'fix_message_delete_modal' : 'Для удаления сообщения введите \'SUBMIT\'',
	'fix_message_delete_submit' : 'Подтвердить удаление',
	'fix_message_delete_error' : 'Ошибка : удаление сообщения отменено!',
	'fix_message_delete_successful' : 'Сообщение удалено!',
	'fix_message_choose' : 'Выберите сообщение',
	'fix_message_message_not_exists' : 'Ошибка : это сообщение больше не существует!',
	'fix_message_change_message' : 'Изменить сообщение',
	'fix_message_modal_title' : 'Название игры',
	'fix_message_modal_description' : 'Описание игры',
	'fix_message_modal_url' : 'Ссылка на игру в Epic Games Store',
	'fix_message_modal_price' : 'Цена на игру',
	'fix_message_modal_key' : 'Доступ раздачи в РФ, \'ru\' или \'not_ru\'',
	'fix_message_button_delete' : 'Удалить сообщение',
	'fix_message_how_view_now' : 'Как сейчас выглядит сообщение',
	'fix_message_no_messages' : 'Нет сообщений, которые можно изменить/удалить',
	'send_to_channel_choose' : 'Выберите канал, куда перебросить пользователя с ником',
	'send_to_channel_sorry' : 'Извините',
	'send_to_channel_no_voice' : 'должен находиться в голосовом канале',
	'send_to_channel_will_be_sent' : 'будет переброшен в',
	'send_to_channel_channel' : '',
	'send_to_channel_check_all' : 'Посмотреть все голосовые каналы',
	'give_permissions_describe' : 'True - выдать полномочия для управления ботом, False - забрать их',
	'give_permissions_all_ready' : 'Всё готово',
	'give_permissions_new_status' : 'Получает новый статус',
	'give_permissions_error_bot' : 'Ошибка : нельзя наделить или забрать полномочия бота для использования UniBot',
	'dont_have_permissions' : 'У вас недостаточно полномочий для использования этой команды',
	'something_went_wrong' : 'Упс... Произошла ошибка! Если у вас есть возможность, напишите разработчику, желательно опишите, при каких обстоятельствах произошла ошибка.',
	'bot_latency' : 'Задержка бота',
	'help_title' : 'Меню помощи по командам',
	'help_footer' : 'Команды доступные пользователям | Все команды работают внутри сообществ',
	'help_commands' : {
		'settings' : {
			'name' : 'uni_settings',
			'description' : '(Команда доступная для пользователей с правом \'Управлять каналами\')\nОсновные настройки бота для сообщества из которого вызвали команду.',
		},
		'fix_message' : {
			'name' : 'uni_fix_message',
			'description' : '(Команда доступная для пользователей с правом \'Управлять каналами\')\nУправление сообщениями, с раздачами, которые всё ещё активны. Можно изменить название/описание/цену/регион раздачи/ссылку на игру, а также удалить сообщение, через бота.',
		},
		'ping' : {
			'name' : 'uni_ping',
			'description' : 'Можно узнать текущую задержку бота.',
		}
	},
	'admin_settings' : 'Настройки для администрации',
	'admin_settings_embed_title' : 'Выбор ролей / пользователей, для доступа к UniBot',
	'admin_settings_choose_role' : 'Выберите роли',
	'admin_settings_choose_user' : 'Выберите пользователей',
	'admin_settings_embed_roles' : 'Роли',
	'admin_settings_embed_users' : 'Пользователи'
}