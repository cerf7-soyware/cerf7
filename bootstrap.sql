INSERT INTO character (handle, first_name, last_name)
VALUES ('omegarofl', 'Алистар', 'Протосский');


INSERT INTO initial_user_in_game_state (datetime, datastore, is_online)
VALUES ('2018-12-20', '{}', FALSE);


-- setup conversation

INSERT INTO conversation (opponent_id, is_required)
VALUES (1, TRUE);

INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 0, 1, 1, '{"text": "Привет"}');
INSERT INTO event (event_type)
VALUES ('NPC_MESSAGE');
INSERT INTO npc_message_event (conversation_id, from_state, to_state, event_id)
VALUES (1, 0, 1, 1);
INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 1, 2, 1, '{"text": "Я тут короче хуярю сок маракуйи"}');
INSERT INTO event (event_type)
VALUES ('NPC_MESSAGE');
INSERT INTO npc_message_event (conversation_id, from_state, to_state, event_id)
VALUES (1, 1, 2, 2);
INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 2, 3, 1, '{"text": "Ебейшая штука как понимаешь"}');
INSERT INTO event (event_type)
VALUES ('NPC_MESSAGE');
INSERT INTO npc_message_event (conversation_id, from_state, to_state, event_id)
VALUES (1, 2, 3, 3);
INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 3, 4, 1, '{"text": "Довольно плотная"}');
INSERT INTO event (event_type)
VALUES ('NPC_MESSAGE');
INSERT INTO npc_message_event (conversation_id, from_state, to_state, event_id)
VALUES (1, 3, 4, 4);
INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 4, 5, 1, '{"text": "Как плотность мысли этого диалога"}');
INSERT INTO event (event_type)
VALUES ('NPC_MESSAGE');
INSERT INTO npc_message_event (conversation_id, from_state, to_state, event_id)
VALUES (1, 4, 5, 5);

INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 5, 6, NULL, '{"text": "Пока нахуй"}');
INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 5, 10, NULL, '{"text": "Глубоко"}');

INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 6, 7, 1, '{"text": "Ебать ты гнида конечно"}');
INSERT INTO event (event_type)
VALUES ('NPC_MESSAGE');
INSERT INTO npc_message_event (conversation_id, from_state, to_state, event_id)
VALUES (1, 6, 7, 6);
INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 7, 8, NULL, '{"text": "Ну я и че"}');
INSERT INTO event (event_type)
VALUES ('NPC_MESSAGE');
INSERT INTO npc_message_event (conversation_id, from_state, to_state, event_id)
VALUES (1, 7, 8, 7);
INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 8, 9, 1, '{"text": "110 000"}');
INSERT INTO event (event_type)
VALUES ('NPC_MESSAGE');
INSERT INTO npc_message_event (conversation_id, from_state, to_state, event_id)
VALUES (1, 8, 9, 8);

INSERT INTO conversation_message (conversation_id, from_state, to_state, sender_id, message_body)
VALUES (1, 10, 11, 1, '{"text": "да я стебусь просто retard 00000"}');
INSERT INTO event (event_type)
VALUES ('NPC_MESSAGE');
INSERT INTO npc_message_event (conversation_id, from_state, to_state, event_id)
VALUES (1, 10, 11, 9);


-- events

INSERT INTO event (event_type)
VALUES ('MAIN_CHARACTER_BACK_ONLINE');

INSERT INTO event (event_type)
VALUES ('NEW_CONVERSATION');

INSERT INTO NEW_CONVERSATION_event (event_id, conversation_id)
VALUES (11, 1);


-- setup scheduling

INSERT INTO initial_scheduling (event_id, event_datetime)
VALUES (10, '2018-12-20 07:38:15');

INSERT INTO initial_scheduling (event_id, event_datetime)
VALUES (11, '2018-12-20 07:19:10');
