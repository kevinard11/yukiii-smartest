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

    /**
     * @var HealthCheckService
     */
    // public $healthCheckService = $this->ea->construct('ada');
    // public $healthCheckServices = $this->ea->construct('ada');

    // public function __construct(HealthCheckService $healthCheckService)
    // {
    //     $this->healthCheckService = $healthCheckService;
    //     $this->healthCheckService->checkConnectivity();
    //     $this->healthCheckService->checkConnectivityssss();

    //     return $this->bar('asdad', b);
    // }

    public function __invoke(Request $request): int
    {
        // $checks = [];
        // try {
        //     $this->healthCheckService->checkConnectivity();
        //     $checks['pdo_connectivity'] = true;
        //     $basda = 'asdasdasd';
        // } catch (\PDOException $e) {
        //     $checks['pdo_connectivity'] = false;
        // }

        // $this->logger->info('Health-Check', $checks);

        // if ($x > 10) {
        //     $this->healthCheckService->checkConnectivity();
        // } else if ($x < 10) {
        //     $checks['pdo_connectivity'] = true;
        // } else {
        //     $basda = 'asdasdasd';
        // }

        // while ($y < 5) {
        //     $basda = 'asdasdasd';
        //     $this->healthCheckService->checkConnectivity();
        // }

        for ($i = 0; $i < 10; $i++) {
            $basda = 'asdasdasd';
            $this->healthCheckService->checkConnectivity();
        }

        return new JsonResponse($checks, $checks['pdo_connectivity'] ? Response::HTTP_OK : Response::HTTP_BAD_REQUEST);
    }
}
