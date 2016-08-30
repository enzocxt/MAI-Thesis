#!/usr/bin/gnuplot
set terminal png enhanced font 'Helvetica' 20
set xrange[20:40]
set yrange[1:3000]
set xlabel 'Support (%)'
set ylabel 'Time (s)'
set logscale y 2

set output 'time_cost_idp.png'

plot 'time_cost_idp.dat' with linespoints title 'eclat+IDP'
