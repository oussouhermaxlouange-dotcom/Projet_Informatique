<?php
declare(strict_types=1);

namespace App\Controllers;

use App\Services\HealthService;
use App\Support\Response;

final class HealthController
{
    public function index(): Response
    {
        $etat = (new HealthService())->verifier();

        return new Response($etat['statut'] === 'ok' ? 200 : 503, $etat);
    }
}
