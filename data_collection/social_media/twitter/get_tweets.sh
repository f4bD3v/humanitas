m[0]='humaniac@humanitas1.cloudapp.net'
m[1]='josephboyd@humanitas2.cloudapp.net'
m[2]='humanitas3@humanitas3.cloudapp.net'
m[3]='humaniac@humanitas4.cloudapp.net'
m[4]='h5@humanitas5.cloudapp.net'
m[5]='humaniac@humanitas6.cloudapp.net'
m[6]='humaniac@humanitas7.cloudapp.net'
m[7]='fabbrix@humanitas8.cloudapp.net'

k[0]='uU56V5a139qqcjPfAKUeG1UXD'
k[1]='aylam3pBvHkhOUmycOWw'
k[2]='pdSvpPsuBfT9R21ii6KPqw'
k[3]='hY83pr25xd95tPz1S98L6ZEOE'
k[4]='FnhKTRfCgpHKMsFwetVbNUtGc'
k[5]='67lCcSq3FUpWBbsZk1IUVlFAY'
k[6]='ga4lAwhQL5TbOkPJtCtjGh823'
k[7]='AwsZtQnXmFnD4KXG98EhObgJQ'

s[0]='V1ltcFIr8vaausLHky5mpWb0JM035lGf17kKST9bIbpB6CPhu6'
s[1]='uXAuZwGX8FUno0P54gdIlGnkijhkY56lVFxRwgjgI'
s[2]='X1nyXfoLsYWeMhM01rRgwlskfmFPEo60mq5QUszBwo8'
s[3]='z5DqCLiECxYXinmwAPBBklGY2P4t8CVBRqsSKuT8hsAAL7l5ze'
s[4]='yqeWtr8ST9ewzhvjleWED0UGxgzX5EEMu9YltO5uEnVr7srqdg'
s[5]='mcgxMMI3aTTAuDOwEgUiVfBtp1in3sLj0XyicGHrMe8zDDmsyj'
s[6]='fzK7HgQqzUkTlurqD0dyW2AfIIhiAEqb5jGwqHDESR6te89S5a'
s[7]='hoKbTI7uNfMOYaCFQBE4xKhGhVTI2DwnTsuReOgTVE4PefFccq'

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
    python="python TWEET_COLLECTION.py ${k[i]} ${s[i]} ${r[i]} tweets"
    "ssh" ${m[i]} "nohup" $python "&> errorlog.txt &"
done
