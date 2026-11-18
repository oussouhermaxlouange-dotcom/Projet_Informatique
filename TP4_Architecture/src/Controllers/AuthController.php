<?php
declare(strict_types=1);

namespace App\Controllers;

use App\Services\AuthService;
use App\Support\Request;
use App\Support\Response;

final class AuthController
{
    public function connecter(Request $requete): Response
    {
        $utilisateur = (new AuthService())->connecter($requete->corpsValide());

        return new Response(200, ['utilisateur' => $utilisateur]);
    }

    public function deconnecter(): Response
    {
        (new AuthService())->deconnecter();

        return new Response(200, ['statut' => 'deconnecte']);
    }

    public function moi(): Response
    {
        $utilisateur = (new AuthService())->exigerUtilisateur();

        return new Response(200, ['utilisateur' => $utilisateur]);
    }
}
