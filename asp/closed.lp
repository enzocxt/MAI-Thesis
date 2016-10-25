tail(T,P,X)   :- seq(T,P,E), slot(X),
                 { seq(T,P+1,F) } 0.
tail(T,P-1,X) :- tail(T,P,X-1), 1 < P,
                 slot(X).
tail(T,P-1,X) :- tail(T,P,X), 1 < P,
                 seq(T,P,E), not pat(X,E).

ins(T,X,E) :- seq(T,P,E), inc(T,P,X),
              not tail(T,P,X).
ins(T,X,E) :- item(E), X = 0..max,
              seq(T,1,F), not cover(T).
:- item(E), X = 0..max,
   ins(T,X,E) : seq(T,1,F).
