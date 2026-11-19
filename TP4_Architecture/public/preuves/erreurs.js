/* Rend les trois erreurs demandées avec le composant partagé (assets/api.js). */
(function () {
  'use strict';

  var exemples = [
    ['e400', 400, {
      erreur: {
        code: 'JSON_INVALIDE',
        message: 'Le corps de la requête doit être un objet JSON valide.'
      }
    }],
    ['e401', 401, {
      erreur: {
        code: 'NON_AUTHENTIFIE',
        message: 'Authentification requise.'
      }
    }],
    ['e500', 500, {
      erreur: {
        code: 'ERREUR_INTERNE',
        message: 'Erreur interne du serveur.'
      }
    }]
  ];

  exemples.forEach(function (exemple) {
    var region = document.getElementById(exemple[0]);
    Messages.afficher(region, { statut: exemple[1], corps: exemple[2] });
  });
})();
