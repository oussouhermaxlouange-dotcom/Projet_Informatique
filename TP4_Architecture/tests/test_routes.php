<?php
declare(strict_types=1);

use App\Support\ApiException;
use App\Support\Env;
use App\Support\Request;
use App\Support\Response;
use App\Support\Router;
use App\Support\Session;

require dirname(__DIR__) . '/src/autoload.php';
Env::load(dirname(__DIR__) . '/.env');

/** @var Router $router */
$router = require dirname(__DIR__) . '/config/routes.php';

// Session vide : les routes protégées doivent répondre 401.
Session::demarrer();
$_SESSION = [];

/**
 * Reproduit la conversion d'exception faite par public/index.php.
 */
$executer = static function (Request $requete) use ($router): Response {
    try {
        return $router->dispatch($requete);
    } catch (ApiException $exception) {
        return Response::erreur(
            $exception->statut,
            $exception->codeErreur,
            $exception->getMessage(),
            $exception->details
        );
    }
};

$cas = [
    [new Request('GET', '/api/sante'), [200, 503], 'santé'],
    [new Request('GET', '/api/inconnue'), [404], 'route inconnue'],
    [new Request('POST', '/api/sante'), [405], 'méthode non autorisée'],
    [new Request('POST', '/api/demandes'), [401], 'création sans session'],
    [new Request('PATCH', '/api/demandes/7/statut'), [401], 'décision sans session'],
    [new Request('GET', '/api/demandes'), [401], 'liste sans session'],
    [new Request('GET', '/api/moi'), [401], 'profil sans session'],
];

echo "Test du routeur\n";
echo "---------------\n";

$echecs = 0;

foreach ($cas as [$requete, $codesAttendus, $libelle]) {
    $reponse = $executer($requete);
    $ok = in_array($reponse->code, $codesAttendus, true);

    printf(
        "%-6s %-32s -> %d  %s  (%s)\n",
        $requete->methode,
        $requete->chemin,
        $reponse->code,
        $ok ? 'OK' : 'ECHEC',
        $libelle
    );

    if (!$ok) {
        $echecs++;
    }

    if ($reponse->code >= 400 && !isset($reponse->corps['erreur'])) {
        echo "       enveloppe d'erreur absente\n";
        $echecs++;
    }
}

if ($echecs > 0) {
    fwrite(STDERR, "ECHEC : {$echecs} cas non conformes\n");
    exit(1);
}

echo "OK  tous les cas sont conformes\n";
exit(0);
