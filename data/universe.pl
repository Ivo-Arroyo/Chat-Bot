framework(rasa, '3.4.17').
framework(rasa, '3.6.8').
framework(rasa, '3.5.16').
framework(rasa, '3.6.7').
framework(rasa, '3.6.6').
framework(rasa, '3.9.5').

framework(dialogflow, '1').
framework(dialogflow, '2').
framework(dialogflow, '3').
framework(dialogflow, '5').

framework(watson, '8').
framework(watson, '2').
framework(watson, '3').
framework(watson, '5').

ultima_version(X,MaxY):-
    findall(Y_temp, framework(X,Y_temp), L_temp),
    max_string(L_temp, MaxY).

max_string([X], X).
max_string([H|T], Max) :-
    max_string(T, MaxRest),
    (H @> MaxRest -> Max = H; Max = MaxRest).

detalle(rasa,'es muy buen frame').
detalle(rasa, 'tiene cosas piolas').

detalle(dialogflow, 'es mejor que rasa').
detalle(dialogflow, 'es mas rapido que los otros').

detalle(watson, 'tiene mucha calidad').
detalle(watson, 'es el mejor frame').

mejora(rasa, '3.9.5', 'La seguridad').
mejora(rasa, '3.9.5', 'La robustez').
mejora(rasa, '3.6.8', 'La eficiencia de busqueda').

mejora(dialogflow, '5' , 'La velocidad de procesamiento').

mejora(watson, '8' , 'un bug problematico antiguo').


compatible(rasa, watson).
compatible(rasa, dialogflow).

compatible(watson, rasa).
compatible(watson, dialogflow).

compatible(dialogflow, rasa).
compatible(dialogflow, watson).



