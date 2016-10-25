#const k=2.
#const max=4.

slot(1..max).
item(E) :- seq(T,P,E).
{ pat(X,E) : item(E) } 1 :- slot(X).

pos(X) :- pat(X,E).
:- not pos(1).
:- pos(X), 2 < X, not pos(X-1).

inc(T,1,X)     :- seq(T,1,E), slot(X),
                  not pos(X+1).
inc(T,P+1,X)   :- seq(T,P,E), inc(T,P,X).
inc(T,P+1,X-1) :- seq(T,P,E), inc(T,P,X),
                  pat(X,E).

cover(T) :- inc(T,P,0), { seq(T,P,E) } 0.
:- not k { cover(T) }.

#show pat/2.
