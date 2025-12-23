# Configs

This is the repository that contains configuration files for the project.

## Docker Compose

Use this command to build the docker compose:
```
docker-compose up --build
```

-------------------------

Also for stopping and deleting the volume(s) - for a fresh start use:
```
docker compose down -v
```

-------------------------

For stopping only and not deleting the volume(s) use:
```
docker compose down
```
-------------------------

For stack use:

```
docker swarm init --advertise-addr <IP_INTERFACE>

docker swarm join --token <TOKEN>

docker stack deploy -c docker-stack.yml idp_music
```
