/* Preuve XSS : on rend deux charges utiles hostiles avec le même composant
   que l'application (assets/rendu.js), puis on vérifie qu'aucun script n'a été
   exécuté. Les charges sont dans ce fichier externe pour que le DOM dumpé ne
   contienne que le résultat du rendu, pas le code de test. */
(function () {
  'use strict';

  var chargeImage = '<img src=x onerror="document.body.dataset.xss=\'image\'">';
  var chargeScript = '<script>document.body.dataset.xss="script"<\/script>';

  var demandes = [{
    id: 999,
    intitule: chargeImage,
    entreprise: chargeScript,
    statut: 'SOUMISE',
    date_debut: '2027-02-01',
    date_fin: '2027-05-31'
  }];

  var verdict = document.getElementById('verdict');

  Rendu.lignesEtudiant(document.getElementById('corps'), demandes);

  var execute = document.body.dataset.xss;
  var images = document.querySelectorAll('tbody img').length;
  var scripts = document.querySelectorAll('tbody script').length;

  if (!execute && images === 0 && scripts === 0) {
    verdict.textContent = 'Aucune exécution : les balises sont affichées comme du texte.';
  } else {
    verdict.textContent = 'ÉCHEC : une balise a été interprétée.';
    verdict.className = 'notice notice-error';
  }
})();
