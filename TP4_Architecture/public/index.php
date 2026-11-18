<?php
declare(strict_types=1);

/**
 * Point d'entrée unique (front controller).
 * Toute requête HTTP passe ici ; aucun accès direct aux classes src/.
 */

use App\Repositories\DatabaseIndisponibleException;
use App\Support\ApiException;
use App\Support\Env;
use App\Support\Request;
use App\Support\Response;
use App\Support\Router;

require dirname(__DIR__) . '/src/autoload.php';

Env::load(dirname(__DIR__) . '/.env');
date_default_timezone_set('UTC');

// Évite d'exposer la version de PHP dans les en-têtes.
header_remove('X-Powered-By');

$requete = Request::depuisGlobals();

try {
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
