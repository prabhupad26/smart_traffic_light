### Start kafka

> `docker-compose up`
> 
> `docker-compose exec kafka bash`
> 
> Create the topic: 
> 
> `kafka-topics.sh --bootstrap-server localhost:9092 --create --topic videotest --partitions 4 --replication-factor 1`
> 
> Describe the topic
> 
> `kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic users`
> 
> Produce
> 
> `kafka-console-producer.sh --bootstrap-server localhost:9092 --property key.separator=, --property parse.key=true --topic sampletopic`
> 
> 
> 
> Consume data from the topic:
> 
>  `kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic videotest --from-beginning`