INSERT INTO character (handle, first_name, last_name)
VALUES ('omegarofl', 'Алистар', 'Протосский');


INSERT INTO initial_user_in_game_state (in_game_date_time, datastore, main_character_is_online)
VALUES ('2018-12-20', '{}', FALSE);


-- setup conversation

INSERT INTO conversation (opponent_id, is_required)
VALUES (1, TRUE);

INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_json)
VALUES (1, 0, 1, 1, '{"text": "Привет"}');

INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_json)
VALUES (1, 1, 2, NULL, '{"text": "Пока нахуй"}');

INSERT INTO conversation_terminal_state (conversation_id, conversation_state)
VALUES (1, 2);


-- events

INSERT INTO event (event_type)
VALUES ('MAIN_CHARACTER_BACK_ONLINE');

INSERT INTO event (event_type)
VALUES ('ADD_CONVERSATION');

INSERT INTO add_conversation_event (event_id, conversation_id)
VALUES (2, 1);


-- setup scheduling

INSERT INTO initial_scheduling (event_id, event_date_time)
VALUES (1, '2018-12-20 07:38:15');

INSERT INTO initial_scheduling (event_id, event_date_time)
VALUES (2, '2018-12-20 07:19:10');
