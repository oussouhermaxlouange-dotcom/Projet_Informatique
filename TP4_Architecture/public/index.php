<?php
declare(strict_types=1);

/**
 * Point d'entrée unique (front controller).
 * Toute requête HTTP passe ici ; aucun accès direct aux classes src/.
 */

use App\Repositories\DatabaseIndisponibleException;
use App\Support\ApiException;
use App\Support\Csrf;
use App\Support\Env;
use App\Support\Request;
use App\Support\Response;
use App\Support\Router;

require dirname(__DIR__) . '/src/autoload.php';

// Serveur intégré de PHP : les fichiers réels (HTML, CSS, JS) sont servis
// directement, seules les routes /api/... arrivent au front controller.
if (PHP_SAPI === 'cli-server') {
    $chemin = parse_url((string) ($_SERVER['REQUEST_URI'] ?? '/'), PHP_URL_PATH);

    if (is_string($chemin)) {
        if ($chemin === '/') {
            header('Content-Type: text/html; charset=utf-8');
            readfile(__DIR__ . '/index.html');
            return;
        }

        if (!str_contains($chemin, '..') && is_file(__DIR__ . $chemin)) {
            return false;
        }
    }
}

Env::load(dirname(__DIR__) . '/.env');
date_default_timezone_set('UTC');

// Évite d'exposer la version de PHP dans les en-têtes.
header_remove('X-Powered-By');

$requete = Request::depuisGlobals();

try {
    // Refuse les écritures venues d'un autre site avant tout traitement.
    Csrf::verifier($requete, $_SERVER);

    /** @var Router $router */
    $router = require dirname(__DIR__) . '/config/routes.php';
    $reponse = $router->dispatch($requete);
} catch (ApiException $exception) {
    // Erreur métier attendue : code HTTP et message déjà rédigés pour le client.
    $reponse = Response::erreur(
        $exception->statut,
        $exception->codeErreur,
        $exception->getMessage(),
        $exception->details
    );
} catch (DatabaseIndisponibleException $exception) {
    error_log('Base indisponible : ' . $exception->getMessage());
    $reponse = Response::erreur(
        503,
        'BASE_INDISPONIBLE',
        'Base de données indisponible.'
    );
} catch (Throwable $exception) {
    // Détail journalisé côté serveur uniquement : pas de fuite de configuration.
    error_log('Erreur non gérée : ' . $exception->getMessage());
    $reponse = Response::erreur(500, 'ERREUR_INTERNE', 'Erreur interne du serveur.');
}

$reponse->envoyer();
