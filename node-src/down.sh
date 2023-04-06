cd /home/ubuntu/chatbot/node-src || exit

docker compose down || exit

docker ps -a | grep "node-src-*" | awk '{print $7}' | while read -r line; do
  echo 'find container: ' "$line" ', removing.'
  docker rm "$line"
done

docker images | grep "node-src-*" | awk '{print $1}' | while read -r line; do
  echo 'find images: ' "$line" ', removing.'
  docker rmi "$line"
done

