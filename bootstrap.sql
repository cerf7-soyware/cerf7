INSERT INTO character (handle, first_name, last_name)
VALUES ('omegarofl', 'Алистар', 'Протосский');


INSERT INTO initial_user_in_game_state (in_game_date_time, datastore, main_character_is_online)
VALUES ('2018-12-20', '{}', FALSE);


-- setup conversation

INSERT INTO conversation (opponent_id, is_required)
VALUES (1, TRUE);

INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 0, 1, 1, '{"text": "Привет"}');
INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 1, 2, 1, '{"text": "Я тут короче хуярю сок маракуйи"}');
INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 2, 3, 1, '{"text": "Ебейшая штука как понимаешь"}');
INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 3, 4, 1, '{"text": "Довольно плотная"}');
INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 4, 5, 1, '{"text": "Как плотность мысли этого диалога"}');

INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 5, 6, NULL, '{"text": "Пока нахуй"}');
INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 5, 7, NULL, '{"text": "Глубоко"}');


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
