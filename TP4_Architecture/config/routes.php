<?php
declare(strict_types=1);

use App\Controllers\AuthController;
use App\Controllers\DemandeController;
use App\Controllers\HealthController;
use App\Support\Request;
use App\Support\Response;
use App\Support\Router;

/**
 * Table des routes de l'API.
 * Toutes les réponses sont du JSON ; aucune page HTML n'est servie ici.
 */
$router = new Router();

$router->add(
    'GET',
    '/api/sante',
    static fn (array $parametres, Request $requete): Response => (new HealthController())->index()
);

$router->add(
    'POST',
    '/api/connexion',
    static fn (array $parametres, Request $requete): Response => (new AuthController())->connecter($requete)
);

$router->add(
    'POST',
    '/api/deconnexion',
    static fn (array $parametres, Request $requete): Response => (new AuthController())->deconnecter()
);

$router->add(
    'GET',
    '/api/moi',
    static fn (array $parametres, Request $requete): Response => (new AuthController())->moi()
);

$router->add(
    'GET',
    '/api/demandes',
    static fn (array $parametres, Request $requete): Response => (new DemandeController())->lister($requete)
);

$router->add(
    'GET',
    '/api/demandes/{id}',
    static fn (array $parametres, Request $requete): Response => (new DemandeController())->detail(
        (int) $parametres['id'],
        $requete
    )
);

$router->add(
    'POST',
    '/api/demandes',
    static fn (array $parametres, Request $requete): Response => (new DemandeController())->creer($requete)
);

$router->add(
    'PATCH',
    '/api/demandes/{id}/statut',
    static fn (array $parametres, Request $requete): Response => (new DemandeController())->changerStatut(
        (int) $parametres['id'],
        $requete
    )
);

return $router;
