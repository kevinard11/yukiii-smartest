// shebang is not used in golang
// /home/utils/go-1.9.4/bin/go run example.go

package test

import (
	"fmt"
	"github.com/streadway/amqp"
	"io/ioutil"
	"net/http"
	"github.com/go-resty/resty/v2"
)


// // main program
// var globalRunCount int
// var globalList [2]string
// var globalArr = []int{1, 2, 3}
// var globalMap = map[string]int{"a": bar(), "b": 20}
// var rabbitReady = 2

// var (
// 	amqpUri          string = "12"
// 	rabbitChan       *amqp.Channel
// 	rabbitCloseError chan *amqp.Error
// 	rabbitReady      chan bool
// 	errorPercent     int

// 	dataCenters = []string{
// 		"asia-northeast2",
// 		"asia-south1",
// 		"europe-west3",
// 		"us-east1",
// 		"us-west1",
// 	}
// )

// type Gost struct {
//     Field1 string
//     Field2 int `default:true`
// }

// var logger = LoggerFactory.getLogger(Controller.class)  // Logger dengan method call
// bar("adas", b)

// func connectToRabbitMQ(uri string, uris *int) amqp.Connection {
// 	for {
// 		conn, err := amqp.Dial(uri)
// 		if err == nil {
// 			return conn
// 		}

// 		log.Println(err)
// 		log.Printf("Reconnecting to %s\n", uri)
// 		time.Sleep(1 * time.Second)
// 	}
// }

func (s *Server) Run() error {

	s.uuid = uuid.New().String()

	return srv.Serve(lis)
}


// func bar(myList *string) string {
// 	// a = globalRunCount + 1 + 2
// 	// if globalRunCount < 2 {
// 	// 	bar(myList)
// 	// }
// 	fmt.Println("hello")
// 	a := baz("a", "b")
// 	return 'b'
// }

// func multiply(x int, y int) int {
//     product := x * y
//     return product
// }

// func processSale(parentSpan ot.Span) {
	// for {
	// 	tracer := ot.GlobalTracer()
	// 	span := tracer.StartSpan("processSale", ot.ChildOf(parentSpan.Context()))
	// 	defer span.Finish()
	// 	span.SetTag(string(ext.SpanKind), "intermediate")
	// 	span.LogFields(otlog.String("info", "Order sent for processing"))
	// 	time.Sleep(time.Duration(42+rand.Int63n(42)) * time.Millisecond)
	// }
	// if bar() {
	// 	m := f.(map[string]interface{})
	// 	id = m["orderid"].(string)
	// } else if tes(){
	// 	fmt.Println("asda")
	// } else {
	// 	fmt.Println("eaaaaa")
	// }

	// for i := 0; i < 5; i++ {
	// 	fmt.Println("Iteration:", i)
	// 	if bar() {
	// 		m := f.(map[string]interface{})
	// 		id = m["orderid"].(string)
	// 	} else if tes(){
	// 		fmt.Println("asda")
	// 	} else {
	// 		fmt.Println("eaaaaa")
	// 	}
	// }
// }

// func main() {
// 	resp, err := http.Get("https://api.example.com/data")
// 	if err != nil {
// 		fmt.Println("Error:", err)
// 		return
// 	}
// 	defer resp.Body.Close()

// 	body, _ := ioutil.ReadAll(resp.Body)
// 	fmt.Println(string(body))

// 	url := "https://api.example.com/data"
// 	jsonData := []byte(`{"name": "John", "email": "john@example.com"}`)

// 	resp, err = http.Post(url, "application/json", bytes.NewBuffer(jsonData))
// 	if err != nil {
// 		fmt.Println("Error:", err)
// 		return
// 	}
// 	defer resp.Body.Close()

// 	client := resty.New()
// 	resp, err = client.R().Get("https://gateway-gc.bfi.co.id/bfibravo/cloud/agency_api/api")

// 	if err != nil {
// 		fmt.Println("Error:", err)
// 		return
// 	}

// 	fmt.Println(resp.String())

// 	resp, err = client.R().
// 		SetHeader("Content-Type", "application/json").
// 		SetBody(map[string]string{"name": "John", "email": "john@example.com"}).
// 		Post("https://gateway-gc.bfi.co.id/confins")

// 	if err != nil {
// 		fmt.Println("Error:", err)
// 		return
// 	}

// 	fmt.Println(resp.String())

// 	client = retryablehttp.NewClient()
// 	resp, err = client.Get("https://microservices.dev.bravo.bfi.co.id/master")
// 	if err != nil {
// 		fmt.Println("Error:", err)
// 		return
// 	}
// 	defer resp.Body.Close()

// 	fmt.Println(resp.Status)
// }

// func main1() {
// 	conn, err := amqp.Dial("amqp://guest:guest@localhost:5672/")
// 	if err != nil {
// 		log.Fatal(err)
// 	}
// 	defer conn.Close()

// 	ch, err := conn.Channel()
// 	if err != nil {
// 		log.Fatal(err)
// 	}
// 	defer ch.Close()

// 	queue, err := ch.QueueDeclare(
// 		"agent_queue",
// 		false,
// 		false,
// 		false,
// 		false,
// 		nil,
// 	)
// 	if err != nil {
// 		log.Fatal(err)
// 	}

// 	body := "Hello, RabbitMQ!"
// 	err = ch.Publish(
// 		"",
// 		queue.Name,
// 		false,
// 		false,
// 		amqp.Publishing{
// 			ContentType: "text/plain",
// 			Body:        []byte(body),
// 		},
// 	)
// 	if err != nil {
// 		log.Fatal(err)
// 	}

// 	fmt.Println(" [x] Sent:", body)
// }

// func main() {
// 	writer := kafka.NewWriter(kafka.WriterConfig{
// 		Brokers:  []string{"localhost:9092"},
// 		Topic:    "master_queue",
// 		Balancer: &kafka.LeastBytes{},
// 	})

	// err := writer.WriteMessages(context.Background(), kafka.Message{
	// 	Key:   []byte("Key"),
	// 	Value: []byte("Hello, Kafka!"),
	// })
	// if err != nil {
	// 	log.Fatal("Failed to write message:", err)
	// }

	// fmt.Println(" [x] Sent: Hello, Kafka!")
	// writer.Close()
// }


// func (app Application) Routes() http.Handler {
// 	var router = httprouter.New()
// 	secure := alice.New(app.checkToken)

// 	router.HandlerFunc(http.MethodPost, "/v1/auth/signin", app.SignIn)

// 	router.HandlerFunc(http.MethodGet, "/v1/movies", app.getAllMovies)
// 	router.HandlerFunc(http.MethodGet, "/v1/movies/:id", app.getOneMovies)
// 	// router.HandlerFunc(http.MethodGet, "/v1/admin/status", app.statusHandler)
// 	router.HandlerFunc(http.MethodPost, "/v1/admin/movies", app.createMovie)
// 	router.HandlerFunc(http.MethodPut, "/v1/admin/movies/:id", app.editMovie)

// 	router.GET("/v1/admin/status", app.wrapMiddleware(secure.ThenFunc(app.statusHandler)))

// 	return app.enableCORS(router)
// }


