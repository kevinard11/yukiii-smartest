<?php

// declare(strict_types=1);

// namespace Instana\RobotShop\Ratings\Controller;

// use Instana\RobotShop\Ratings\Service\HealthCheckService;
// use Psr\Log\LoggerAwareInterface;
// use Psr\Log\LoggerAwareTrait;
// use Symfony\Component\HttpFoundation\JsonResponse;
// use Symfony\Component\HttpFoundation\Request;
// use Symfony\Component\HttpFoundation\Response;
// use Symfony\Component\Routing\Annotation\Route;


// require 'vendor/autoload.php';
// use GuzzleHttp\Client;
// use Unirest\Request;
// use Symfony\Component\HttpClient\HttpClient;

/**
 * @Route("/_health")
 */
class HealthController implements LoggerAwareInterface
{
    // use LoggerAwareTrait;

    // /**
    //  * @var string
    //  */
    // private $dsn;

    // /**
    //  * @var string
    //  */
    // private $user;

    // /**
    //  * @var string
    //  */
    // private $password;

    // public function __construct(string $dsn, string $user, string $password)
    // {
    //     $this->dsn = $dsn;
    //     $this->user = $user;
    //     $this->password = $password;
    // }

    // public function getConnection(): PDO
    // {
    //     // $opt = [
    //     //     PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    //     //     PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    //     //     PDO::ATTR_EMULATE_PREPARES => false,
    //     // ];

    //     // try {
    //     //     return new PDO($this->dsn, $this->user, $this->password, $opt);
    //     // } catch (PDOException $e) {
    //     //     $msg = $e->getMessage();
    //     //     $this->logger->error("Database error $msg");

    //     //     return null;
    //     // }

    //     $url = "https://gateway-gc.bfi.co.id/confins/asdadasda";
    //     $response = file_get_contents($url);
    //     $data = json_decode($response, true);

    //     print_r($data);
    //     $url = "https://microservices.dev.bravo.bfi.co.id/master";
    //     $data = ["name" => "John", "email" => "john@example.com"];

    //     $ch = curl_init($url);
    //     curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    //     curl_setopt($ch, CURLOPT_POST, true);
    //     curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    //     curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));

    //     $response = curl_exec($ch);
    //     curl_close($ch);

    //     $result = json_decode($response, true);
    //     print_r($result);

    //     $client = new Client();
    //     $response = $client->request('GET', 'https://api.example.com/data');
    //     $data = json_decode($response->getBody(), true);

    //     print_r($data);

    //     $response = Request::get('https://api.example.com/data');
    //     $data = $response->body;

    //     print_r($data);

    //     $client = HttpClient::create();
    //     $response = $client->request('GET', 'https://api.example.com/data');

    //     $data = $response->toArray();
    //     print_r($data);

    //     $channel->queue_declare('master_queue', false, false, false, false);
    //     $queue = $context->createQueue('master_queue');
    //     $conf = new RdKafka\Conf();
    //     $conf->set('master_queue', 'localhost:9092');

    //     $producer = new RdKafka\Producer($conf);
    //     $topic = $producer->newTopic("test-topic");
    // }


    // #@Route("/fetch/{sku}", methods={"POST"})
    // public function get(Request $request, string $sku): Response
    // {
    //     try {
    //         if (!$this->ratingsService->ratingBySku($sku)) {
    //             throw new NotFoundHttpException("$sku not found");
    //         }
    //     } catch (\Exception $e) {
    //         throw new HttpException(500, $e->getMessage(), $e);
    //     }

    //     return new JsonResponse($this->ratingsService->ratingBySku($sku));
    // }
    
    /**
     * @Route(path="/rate/{sku}/{score}", methods={"PUT"})
     */
    public function put(Request $request, string $sku, int $score): Response
    {
        $score = min(max(1, $score), 5);

        try {
            if (false === $this->catalogueService->checkSKU($sku)) {
                throw new NotFoundHttpException("$sku not found");
            }
        } catch (\Exception $e) {
            throw new HttpException(500, $e->getMessage(), $e);
        }

        try {
            $rating = $this->ratingsService->ratingBySku($sku);
            if (0 === $rating['avg_rating']) {
                // not rated yet
                $this->ratingsService->addRatingForSKU($sku, $score);
            } else {
                // iffy maths
                $newAvg = (($rating['avg_rating'] * $rating['rating_count']) + $score) / ($rating['rating_count'] + 1);
                $this->ratingsService->updateRatingForSKU($sku, $newAvg, $rating['rating_count'] + 1);
            }

            return new JsonResponse([
                'success' => true,
            ]);
        } catch (\Exception $e) {
            throw new HttpException(500, 'Unable to update rating', $e);
        }
    }

}
