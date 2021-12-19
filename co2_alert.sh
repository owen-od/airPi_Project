#!/bin/bash

#use api to get latest CO2 reading for the bedroom and assign to CO2 variable (jq used to read json)
CO2=$(curl -s http://192.168.0.173:5000/home/bedroom | jq -r '.CO2')
echo $CO2

# check if the co2 level is above 1000ppm, and email the user a warning if so
if [ "$CO2" -gt 1000 ]
then
# CO2 is above limit - send alert to user
    swaks --auth \
            --server smtp.mailgun.org \
            --au postmaster@sandbox111aaaabbb222233333cccccdddd5555.mailgun.org \ #enter mailgun username here
            --ap aaaaaaaaaaabbbbbbbbbbbbbbccccccc-22222222-11111111 \ #enter mailgun password here
            --to email@mail.com \ #enter recipient mail here
            --h-Subject: "CO2 level warning" \
            --body "The CO2 level in the bedroom is over 1000ppm (currently $CO2). Open the window!"
fi