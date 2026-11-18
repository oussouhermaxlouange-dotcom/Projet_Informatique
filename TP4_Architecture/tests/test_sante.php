<?php
declare(strict_types=1);

use App\Controllers\HealthController;
use App\Support\Env;
use App\Support\Response;

require dirname(__DIR__) . '/src/autoload.php';
Env::load(dirname(__DIR__) . '/.env');

echo "Test de la route de santé (sans HTTP)\n";
echo "------------------------------------\n";

$reponse = (new HealthController())->index();
$erreurs = [];

if (!in_array($reponse->code, [200, 503], true)) {
    $erreurs[] = 'code HTTP inattendu : ' . $reponse->code;
}

foreach (['statut', 'base', 'horodatage'] as $cle) {
    if (!array_key_exists($cle, $reponse->corps)) {
        $erreurs[] = "clé absente : {$cle}";
    }
}

$statut = $reponse->corps['statut'] ?? null;
if (($reponse->code === 200 && $statut !== 'ok') || ($reponse->code === 503 && $statut !== 'indisponible')) {
    $erreurs[] = 'incohérence entre le code HTTP et le statut';
}

echo 'Code HTTP : ' . $reponse->code . "\n";
echo 'Corps     : ' . json_encode($reponse->corps, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n";

if ($erreurs !== []) {
    fwrite(STDERR, "ECHEC\n- " . implode("\n- ", $erreurs) . "\n");
    exit(1);
}

echo "OK  route de santé conforme\n";
exit(0);
