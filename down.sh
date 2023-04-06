cd /home/ubuntu/chatbot || exit

docker stop "telegram_chatbot" || exit
docker rm "telegram_chatbot" || exit

docker images | grep "chatbot" | awk '{print $1}' | while read -r line; do
  echo 'find images: ' "$line" ', removing.'
  docker rmi "$line"
done

