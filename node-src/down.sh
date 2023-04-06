cd /home/ubuntu/chatbot/node-src || exit

docker compose down || exit

docker images | grep "node-src-*" | awk '{print $1}' | while read -r line; do
  echo 'find images: ' "$line" ', removing.'
  docker rmi "$line"
done

