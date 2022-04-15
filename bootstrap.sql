INSERT INTO character ("handle", "firstName", "lastName")
VALUES ('omegarofl', 'Алистар', 'Протосский');


INSERT INTO initial_user_in_game_state ("inGameDateTime", "datastore", "mainCharacterIsOnline")
VALUES ('2018-12-20', '{}', FALSE);


-- setup conversation

INSERT INTO conversation ("opponentId", "isRequired")
VALUES (1, TRUE);

INSERT INTO conversation_message ("conversationId", "fromState", "toState", "senderId", "messageJson")
VALUES (1, 0, 1, 1, '{"text": "Привет"}');

INSERT INTO conversation_message ("conversationId", "fromState", "toState", "senderId", "messageJson")
VALUES (1, 1, 2, NULL, '{"text": "Пока нахуй"}');

INSERT INTO conversation_terminal_state ("conversationId", "conversationState")
VALUES (1, 2);


-- events

INSERT INTO event ("eventType")
VALUES ('MAIN_CHARACTER_BACK_ONLINE');

INSERT INTO event ("eventType")
VALUES ('ADD_CONVERSATION');

INSERT INTO add_conversation_event ("eventId", "conversationId")
VALUES (2, 1);


-- setup scheduling

INSERT INTO initial_scheduling ("eventId", "eventDateTime")
VALUES (1, '2018-12-20 07:38:15');

INSERT INTO initial_scheduling ("eventId", "eventDateTime")
VALUES (2, '2018-12-20 07:19:10');
