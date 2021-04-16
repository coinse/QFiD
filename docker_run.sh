docker kill expr
docker rm expr
docker build --tag expr:latest .
docker run -dt --name expr expr:latest
docker exec -it expr bash
