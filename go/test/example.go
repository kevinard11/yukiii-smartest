// shebang is not used in golang
// /home/utils/go-1.9.4/bin/go run example.go

package test

import (
	"fmt"
	"github.com/streadway/amqp"
)


// // main program
// var globalRunCount int
// var globalList [2]string
// var globalArr = []int{1, 2, 3}
// var globalMap = map[string]int{"a": bar(), "b": 20}
var rabbitReady = 2

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

// func bar(myList string) string {
// 	// a = globalRunCount + 1 + 2
// 	// if globalRunCount < 2 {
// 	// 	bar(myList)
// 	// }
// 	fmt.Println("hello")
// 	a = baz("a", "b")
// }

func processSale(parentSpan ot.Span) {
	// for {
	// 	tracer := ot.GlobalTracer()
	// 	span := tracer.StartSpan("processSale", ot.ChildOf(parentSpan.Context()))
	// 	defer span.Finish()
	// 	span.SetTag(string(ext.SpanKind), "intermediate")
	// 	span.LogFields(otlog.String("info", "Order sent for processing"))
	// 	time.Sleep(time.Duration(42+rand.Int63n(42)) * time.Millisecond)
	// }
	if bar() {
		m := f.(map[string]interface{})
		id = m["orderid"].(string)
	}
}


