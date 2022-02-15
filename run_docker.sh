docker stop nvr_speecher
docker rm nvr_speecher
docker build -t nvr_speecher .
docker run -d \
 -it \
 --name nvr_speecher \
 -v $HOME/creds:/speecher/creds \
 nvr_speecher
