<?php
declare(strict_types=1);

use App\Repositories\DemandeRepository;
use App\Repositories\UtilisateurRepository;
use App\Services\DemandeService;
use App\Support\ApiException;
use App\Support\Env;

require dirname(__DIR__) . '/src/autoload.php';
Env::load(dirname(__DIR__) . '/.env');

echo "Test du domaine (sans HTTP)\n";
echo "---------------------------\n";

$echecs = 0;

$verifier = static function (string $libelle, bool $condition) use (&$echecs): void {
    printf("%-62s %s\n", $libelle, $condition ? 'OK' : 'ECHEC');

    if (!$condition) {
        $echecs++;
    }
};

// 1. Empreinte bcrypt du jeu d'essai et vérification du mot de passe.
$utilisateurs = new UtilisateurRepository();
$etudiant = $utilisateurs->trouverParEmail('sena.houngbo@univ.test');
$verifier('compte de démonstration trouvé', $etudiant !== null);
$verifier(
    'mot de passe Demo1234! vérifié par password_verify',
    $etudiant !== null && password_verify('Demo1234!', (string) $etudiant['mot_de_passe_hash'])
);
$verifier(
    'empreinte différente du mot de passe en clair',
    $etudiant !== null && $etudiant['mot_de_passe_hash'] !== 'Demo1234!'
);

// 2. Table des transitions.
$service = new DemandeService();
$verifier('BROUILLON -> SOUMISE autorisé', $service->transitionAutorisee('BROUILLON', 'SOUMISE'));
$verifier('SOUMISE -> VALIDEE autorisé', $service->transitionAutorisee('SOUMISE', 'VALIDEE'));
$verifier('SOUMISE -> REFUSEE autorisé', $service->transitionAutorisee('SOUMISE', 'REFUSEE'));
$verifier('VALIDEE -> REFUSEE interdit', !$service->transitionAutorisee('VALIDEE', 'REFUSEE'));
$verifier('BROUILLON -> VALIDEE interdit', !$service->transitionAutorisee('BROUILLON', 'VALIDEE'));
$verifier('statut inconnu sans transition', $service->transitionsDepuis('INCONNU') === []);

// 3. Dépôt : lectures préparées.
$demandes = new DemandeRepository();
$demande = $demandes->findById(3);
$verifier('findById retourne la demande 3', $demande !== null && (int) $demande['id'] === 3);
$verifier('findById expose le statut et l’entreprise', $demande !== null
    && $demande['statut'] === 'VALIDEE'
    && $demande['entreprise'] === 'Studio Kora');
$listeEtudiant = $demandes->findByStudent(1);
$verifier('findByStudent(1) retourne uniquement ses demandes', $listeEtudiant !== []
    && array_reduce(
        $listeEtudiant,
        static fn (bool $ok, array $ligne): bool => $ok && (int) $ligne['etudiant_id'] === 1,
        true
    ));
$verifier('findById(999999) retourne null', $demandes->findById(999999) === null);

// 4. Transaction : rollback complet si l'opération échoue.
$avant = $demandes->findById(3);

try {
    $demandes->transaction(static function () use ($demandes): void {
        $demandes->updateStatus(3, 'REFUSEE', 'Panne simulée', '2026-11-18 00:00:00');
        throw new RuntimeException('panne simulée après la mise à jour');
    });
} catch (RuntimeException) {
    // attendu
}

$apres = $demandes->findById(3);
$verifier(
    'rollback : statut et motif inchangés après échec',
    $avant !== null
    && $apres !== null
    && $avant['statut'] === $apres['statut']
    && $avant['motif_refus'] === $apres['motif_refus']
);

// 5. Refus métier : 409 sur transition interdite, 422 sur motif manquant.
$responsable = ['id' => 6, 'role' => 'RESPONSABLE'];

$code = null;
try {
    $service->changerStatut(5, ['statut' => 'VALIDEE'], $responsable);
} catch (ApiException $exception) {
    $code = $exception->statut;
}
$verifier('REFUSEE -> VALIDEE renvoie 409', $code === 409);

$code = null;
try {
    $service->changerStatut(2, ['statut' => 'REFUSEE'], $responsable);
} catch (ApiException $exception) {
    $code = $exception->statut;
}
$verifier('refus sans motif renvoie 422', $code === 422);

$code = null;
try {
    $service->changerStatut(2, ['statut' => 'VALIDEE'], ['id' => 1, 'role' => 'ETUDIANT']);
} catch (ApiException $exception) {
    $code = $exception->statut;
}
$verifier('étudiant qui décide renvoie 403', $code === 403);

if ($echecs > 0) {
    fwrite(STDERR, "ECHEC : {$echecs} vérification(s) en échec\n");
    exit(1);
}

echo "OK  toutes les vérifications passent\n";
exit(0);
