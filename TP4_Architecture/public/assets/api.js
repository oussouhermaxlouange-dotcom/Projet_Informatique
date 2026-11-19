/* --------------------------------------------------------------------------
   api.js — appels HTTP et messages d'erreur lisibles.
   Aucune balise HTML n'est construite ici : uniquement du texte.
   -------------------------------------------------------------------------- */
(function (global) {
  'use strict';

  class ErreurApi extends Error {
    constructor(statut, corps) {
      super('Erreur API ' + statut);
      this.statut = statut;
      this.corps = corps;
    }
  }

  /**
   * Appelle l'API et renvoie le corps JSON.
   * Lève ErreurApi avec le code HTTP réel ; statut 0 = serveur injoignable.
   */
  async function appeler(chemin, options) {
    const reglages = options || {};
    const entetes = { Accept: 'application/json' };

    if (reglages.corps !== undefined) {
      entetes['Content-Type'] = 'application/json';
    }

    let reponse;

    try {
      reponse = await fetch(chemin, {
        method: reglages.methode || 'GET',
        credentials: 'same-origin',
        headers: entetes,
        body: reglages.corps !== undefined ? JSON.stringify(reglages.corps) : undefined
      });
    } catch (erreur) {
      throw new ErreurApi(0, null);
    }

    let corps = null;
    const type = reponse.headers.get('content-type') || '';

    if (type.indexOf('application/json') !== -1) {
      try {
        corps = await reponse.json();
      } catch (erreur) {
        corps = null;
      }
    }

    if (!reponse.ok) {
      throw new ErreurApi(reponse.status, corps);
    }

    return corps;
  }

  const MESSAGES = {
    0: 'Le serveur ne répond pas. Vérifiez qu’il est démarré.',
    400: 'La requête envoyée est mal formée.',
    401: 'Votre session a expiré ou les identifiants sont incorrects.',
    403: 'Vous n’avez pas les droits pour cette action.',
    404: 'Cette ressource est introuvable.',
    405: 'Cette action n’est pas autorisée sur cette ressource.',
    409: 'Cette décision n’est plus possible : la demande a déjà été traitée.',
    422: 'Certaines valeurs du formulaire sont invalides.',
    500: 'Une erreur interne est survenue. Réessayez dans un instant.',
    503: 'La base de données est indisponible. Réessayez plus tard.'
  };

  /**
   * Transforme une erreur en message lisible : titre + liste de détails.
   * Le message du serveur est préféré quand il existe ; il est déjà en français.
   */
  function expliquer(erreur) {
    const statut = erreur && typeof erreur.statut === 'number' ? erreur.statut : 0;
    const corps = erreur && erreur.corps ? erreur.corps : null;
    const contenu = corps && corps.erreur ? corps.erreur : null;

    const titre = contenu && typeof contenu.message === 'string' && contenu.message !== ''
      ? contenu.message
      : (MESSAGES[statut] || MESSAGES[500]);

    const details = [];

    if (contenu && contenu.code) {
      details.push('Code : ' + contenu.code);
    }

    if (contenu && contenu.details && typeof contenu.details === 'object') {
      Object.keys(contenu.details).forEach(function (champ) {
        const valeur = contenu.details[champ];
        details.push(champ + ' : ' + (typeof valeur === 'string' ? valeur : JSON.stringify(valeur)));
      });
    }

    return { statut: statut, titre: titre, details: details };
  }

  /** Affiche (ou masque) l'alerte globale. */
  function afficher(region, erreur) {
    const titre = region.querySelector('.alerte-titre');
    const liste = region.querySelector('.alerte-details');
    const explication = expliquer(erreur);

    titre.textContent = explication.titre;
    liste.replaceChildren();

    explication.details.forEach(function (texte) {
      const item = document.createElement('li');
      item.textContent = texte;
      liste.appendChild(item);
    });

    region.hidden = false;
    region.dataset.statut = String(explication.statut);
  }

  function masquer(region) {
    if (region) {
      region.hidden = true;
      region.removeAttribute('data-statut');
    }
  }

  global.Api = {
    appeler: appeler,
    ErreurApi: ErreurApi,
    expliquer: expliquer
  };

  global.Messages = {
    afficher: afficher,
    masquer: masquer,
    expliquer: expliquer,
    generique: MESSAGES
  };
})(window);
