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

    public function getConnection(): PDO
    {
        $opt = [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ];

        try {
            return new PDO($this->dsn, $this->user, $this->password, $opt);
        } catch (PDOException $e) {
            $msg = $e->getMessage();
            $this->logger->error("Database error $msg");

            return null;
        }
    }
}
