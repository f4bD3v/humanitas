m[0]='humaniac@humanitas1.cloudapp.net'
m[1]='josephboyd@humanitas2.cloudapp.net'
m[2]='humanitas3@humanitas3.cloudapp.net'
m[3]='humaniac@humanitas4.cloudapp.net'
m[4]='h5@humanitas5.cloudapp.net'
m[5]='humaniac@humanitas6.cloudapp.net'
m[6]='humaniac@humanitas7.cloudapp.net'
m[7]='fabbrix@humanitas8.cloudapp.net'

r[0]='0'
r[1]='1'
r[2]='2'
r[3]='3'
r[4]='4'
r[5]='5'
r[6]='6'
r[7]='7'

for (( i=0; i<=7; i++ ))
do
    "scp" "${r[i]}.pickle" "${m[i]}:tweet_inputs/${r[i]}.pickle"
done
