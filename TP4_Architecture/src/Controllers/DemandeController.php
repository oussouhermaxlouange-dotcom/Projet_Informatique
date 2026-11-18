<?php
declare(strict_types=1);

namespace App\Controllers;

use App\Services\AuthService;
use App\Services\DemandeService;
use App\Support\Request;
use App\Support\Response;

/**
 * Adaptation HTTP des demandes : lire la requête, appeler le service,
 * choisir le code de retour. Aucun SQL ici.
 */
final class DemandeController
{
    public function lister(Request $requete): Response
    {
        $utilisateur = (new AuthService())->exigerUtilisateur();
        $demandes = (new DemandeService())->lister($utilisateur);

        return new Response(200, ['demandes' => $demandes]);
    }

    public function detail(int $id, Request $requete): Response
    {
        $utilisateur = (new AuthService())->exigerUtilisateur();
        $demande = (new DemandeService())->detail($id, $utilisateur);

        return new Response(200, ['demande' => $demande]);
    }

    public function creer(Request $requete): Response
    {
        $utilisateur = (new AuthService())->exigerUtilisateur();
        $demande = (new DemandeService())->creer($requete->corpsValide(), $utilisateur);

        return new Response(201, ['demande' => $demande]);
    }

    public function changerStatut(int $id, Request $requete): Response
    {
        $utilisateur = (new AuthService())->exigerUtilisateur();
        $demande = (new DemandeService())->changerStatut($id, $requete->corpsValide(), $utilisateur);

        return new Response(200, ['demande' => $demande]);
    }
}
