#!/usr/bin/gnuplot
set terminal png enhanced font 'Helvetica' 20
set xrange[10:50]
set yrange[1:20000]
set xlabel 'Support (%)'
set ylabel 'Time (ms)'
set logscale y 2

set output 'time_cost.png'

plot 'time_cost.dat' with linespoints title 'closed eclat', \
'time_cost.dat' using 1:3 with linespoints title 'python post-processing'
