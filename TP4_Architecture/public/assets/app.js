(function () {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const state = { user: null, requests: [], screen: 'vue-connexion', selectedId: null, filter: 'all' };
  const screens = ['vue-connexion', 'vue-liste-etudiant', 'vue-etudiant', 'vue-detail', 'vue-responsable', 'vue-traiter'];
  const fields = { email: 'email', mot_de_passe: 'mot-de-passe', entreprise_id: 'entreprise', intitule: 'intitule', date_debut: 'date-debut', date_fin: 'date-fin', motif: 'motif' };
  const errors = { email: 'erreur-email', mot_de_passe: 'erreur-mot-de-passe', entreprise_id: 'erreur-entreprise', intitule: 'erreur-intitule', date_debut: 'erreur-debut', date_fin: 'erreur-fin', motif: 'erreur-motif' };
  const roleNames = { ETUDIANT: 'Étudiant', RESPONSABLE: 'Responsable', ADMIN: 'Administrateur', ENCADREUR: 'Encadreur', DEVELOPPEUR: 'Développeur' };

  function isManager() { return state.user && ['RESPONSABLE', 'ADMIN'].includes(state.user.role); }
  function homeScreen() { return state.user && (isManager() || state.user.role === 'ENCADREUR') ? 'vue-responsable' : 'vue-liste-etudiant'; }
  function show(screen) {
    if (!state.user && screen !== 'vue-connexion') screen = 'vue-connexion';
    if (screen === 'vue-responsable' && !isManager()) screen = 'vue-liste-etudiant';
    state.screen = screen;
    screens.forEach((id) => { const node = $(id); if (node) node.hidden = id !== screen; });
    $('etat-api').hidden = !$('etat-api').classList.contains('is-error');
    $('navigation').hidden = !state.user;
    document.querySelectorAll('[data-role="student"]').forEach((node) => { node.hidden = !(state.user && ['ETUDIANT', 'ENCADREUR'].includes(state.user.role)); });
    document.querySelectorAll('[data-role="manager"]').forEach((node) => { node.hidden = !isManager(); });
    document.querySelectorAll('.main-nav [data-nav]').forEach((node) => node.classList.toggle('active', node.dataset.nav === ({ 'vue-liste-etudiant': 'mes-demandes', 'vue-etudiant': 'nouvelle-demande', 'vue-responsable': 'demandes-a-traiter' })[screen]));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  function announce(message) { $('zone-succes').textContent = message; $('zone-succes').hidden = false; }
  function clearMessages() {
    $('zone-succes').hidden = true; $('zone-succes').textContent = ''; Messages.masquer($('zone-erreur'));
    Object.keys(errors).forEach((key) => { const note = $(errors[key]); if (note) { note.hidden = true; note.textContent = ''; } const field = $(fields[key]); if (field) field.removeAttribute('aria-invalid'); });
  }
  function renderFieldErrors(error) {
    const details = error && error.corps && error.corps.erreur && error.corps.erreur.details;
    if (!details) return;
    Object.keys(details).forEach((key) => { const note = $(errors[key]); if (!note) return; note.textContent = String(details[key]); note.hidden = false; const input = $(fields[key]); if (input) input.setAttribute('aria-invalid', 'true'); });
  }
  function handleError(error, options) {
    Messages.afficher($('zone-erreur'), error);
    if (error && error.statut === 422 && (!options || options.fields !== false)) renderFieldErrors(error);
    if (error && error.statut === 401 && (!options || options.session !== false)) logout(false);
    if (error && error.statut === 503) setHealth('Base de données indisponible.', false);
  }
  function setHealth(message, ok) {
    $('etat-api').textContent = message; $('etat-api').className = 'status-line ' + (ok ? 'is-ok' : 'is-error');
    $('etat-api').hidden = ok;
    $('etat-badge').textContent = ok ? 'Service actif' : 'Service indisponible';
    $('etat-badge').classList.toggle('offline', !ok);
  }
  function enter(user) {
    state.user = user;
    const name = [user.prenom, user.nom].filter(Boolean).join(' ');
    $('identite').textContent = name;
    $('role-connecte').textContent = roleNames[user.role] || user.role;
    $('zone-session').hidden = false;
    clearMessages(); show(homeScreen()); loadList();
  }
  function renderManagerList() {
    Rendu.cartesResponsable($('liste-responsable'), state.requests, state.user && state.user.role === 'RESPONSABLE', state.filter, $('filtre-demandes').value);
    const visibleCount = $('liste-responsable').children.length;
    $('vide-responsable').textContent = state.requests.length
      ? 'Aucun dossier ne correspond à votre filtre.'
      : 'Aucune demande à afficher.';
    $('vide-responsable').hidden = visibleCount > 0;
  }
  function logout(showMessage) {
    state.user = null; state.requests = []; $('zone-session').hidden = true;
    $('corps-etudiant').replaceChildren(); $('liste-responsable').replaceChildren(); clearMessages(); show('vue-connexion');
    if (showMessage) announce('Vous êtes déconnecté.');
  }
  async function loadList() {
    if (!state.user) return;
    try {
      const response = await Api.appeler('/api/demandes'); state.requests = response && response.demandes ? response.demandes : [];
      if (isManager()) {
        renderManagerList();
        const pending = state.requests.filter((item) => item.statut === 'SOUMISE').length;
        $('compteur-responsable').textContent = pending + ' en attente';
        $('delai-moyen').textContent = state.requests.length + ' dossiers dans la file';
        Rendu.statistiques($('stats-etudiant'), state.requests);
      } else {
        Rendu.lignesEtudiant($('corps-etudiant'), state.requests);
        $('compteur-etudiant').textContent = state.requests.length + (state.requests.length === 1 ? ' convention' : ' conventions');
        $('vide-etudiant').hidden = state.requests.length > 0;
        Rendu.statistiques($('stats-etudiant'), state.requests);
      }
      setHealth('API et base de données disponibles.', true);
    } catch (error) { handleError(error); }
  }
  async function openDetail(id, review) {
    clearMessages(); state.selectedId = Number(id);
    try {
      const response = await Api.appeler('/api/demandes/' + encodeURIComponent(id));
      const item = response.demande;
      const title = 'Convention n° ' + item.id;
      $('titre-detail').textContent = title; $('meta-detail').textContent = 'Dossier enregistré le ' + Rendu.date(item.date_depot) + ' · Statut : ' + Rendu.libelles[item.statut];
      $('statut-detail').replaceChildren(Rendu.badge(item.statut));
      $('detail-etudiant').textContent = item.etudiant || '—'; $('detail-entreprise').textContent = item.entreprise || '—'; $('detail-intitule').textContent = item.intitule || '—'; $('detail-periode').textContent = Rendu.periode(item); $('detail-depot').textContent = Rendu.date(item.date_depot); $('detail-decision').textContent = item.date_decision ? Rendu.date(item.date_decision) : 'En attente';
      $('detail-motif-wrap').hidden = !(item.statut === 'REFUSEE' && item.motif_refus); $('detail-motif').textContent = item.motif_refus || '';
      $('detail-circuit-title').textContent = item.statut === 'SOUMISE' ? 'En attente de décision' : 'Décision enregistrée';
      $('detail-circuit-copy').textContent = item.statut === 'SOUMISE' ? 'Le responsable pédagogique doit encore examiner cette convention.' : 'Le statut et la décision sont conservés dans le dossier.';
      $('progress-step').style.width = item.statut === 'SOUMISE' ? '50%' : '100%';
      $('titre-traiter').textContent = 'Décision de convention : ' + (item.etudiant || 'Étudiant');
      $('meta-traiter').textContent = 'Dossier n° ' + item.id + ' · ' + (item.etudiant || '') + ' · ' + Rendu.date(item.date_depot);
      $('statut-traiter').replaceChildren(Rendu.badge(item.statut));
      $('traiter-etudiant').textContent = item.etudiant || '—'; $('traiter-reference').textContent = 'Convention n° ' + item.id; $('traiter-entreprise').textContent = item.entreprise || '—'; $('traiter-intitule').textContent = item.intitule || '—'; $('traiter-periode').textContent = Rendu.periode(item);
      $('motif').value = item.statut === 'REFUSEE' ? (item.motif_refus || '') : '';
      show(review && isManager() ? 'vue-traiter' : 'vue-detail');
    } catch (error) { handleError(error); }
  }
  async function decide(status) {
    const motif = $('motif').value.trim();
    if (status === 'REFUSEE' && (motif.length < 3 || motif.length > 255)) {
      $('erreur-motif').textContent = 'Le motif doit contenir de 3 à 255 caractères.'; $('erreur-motif').hidden = false; $('motif').setAttribute('aria-invalid', 'true'); $('motif').focus(); return;
    }
    clearMessages();
    const body = { statut: status }; if (status === 'REFUSEE') body.motif = motif;
    try {
      await Api.appeler('/api/demandes/' + state.selectedId + '/statut', { methode: 'PATCH', corps: body });
      announce('Convention n° ' + state.selectedId + ' : ' + Rendu.libelles[status].toLocaleLowerCase('fr') + '.');
      await loadList(); show('vue-responsable');
    } catch (error) { handleError(error); }
  }

  document.querySelectorAll('[data-nav]').forEach((button) => button.addEventListener('click', (event) => {
    event.preventDefault();
    const target = button.dataset.nav;
    if (target === 'home') show(homeScreen());
    else if (target === 'mes-demandes') { show('vue-liste-etudiant'); loadList(); }
    else if (target === 'nouvelle-demande') show('vue-etudiant');
    else if (target === 'demandes-a-traiter') { show('vue-responsable'); loadList(); }
  }));
  document.querySelectorAll('[data-login-role]').forEach((button) => button.addEventListener('click', () => {
    document.querySelectorAll('[data-login-role]').forEach((item) => item.classList.toggle('selected', item === button));
    $('email').value = button.dataset.loginRole === 'ETUDIANT' ? 'sena.houngbo@univ.test' : 'responsable.pedago@univ.test';
    $('mot-de-passe').focus();
  }));
  $('formulaire-connexion').addEventListener('submit', async (event) => {
    event.preventDefault(); clearMessages(); const button = $('connexion-submit'); button.disabled = true;
    try { const response = await Api.appeler('/api/connexion', { methode: 'POST', corps: { email: $('email').value.trim(), mot_de_passe: $('mot-de-passe').value } }); $('formulaire-connexion').reset(); enter(response.utilisateur); announce('Connexion réussie. Bienvenue ' + response.utilisateur.prenom + '.'); }
    catch (error) { handleError(error, { session: false }); } finally { button.disabled = false; }
  });
  $('deconnexion').addEventListener('click', async () => { try { await Api.appeler('/api/deconnexion', { methode: 'POST' }); } catch (_) {} logout(true); });
  $('formulaire-demande').addEventListener('submit', async (event) => {
    event.preventDefault(); clearMessages(); const button = $('envoyer-demande'); button.disabled = true;
    const body = { entreprise_id: Number($('entreprise').value), intitule: $('intitule').value.trim(), date_debut: $('date-debut').value, date_fin: $('date-fin').value, soumettre: $('soumettre').checked };
    try { const response = await Api.appeler('/api/demandes', { methode: 'POST', corps: body }); event.target.reset(); $('soumettre').checked = true; await loadList(); announce('Convention n° ' + response.demande.id + ' enregistrée au statut ' + Rendu.libelles[response.demande.statut] + '.'); show('vue-liste-etudiant'); }
    catch (error) { handleError(error); } finally { button.disabled = false; }
  });
  $('corps-etudiant').addEventListener('click', (event) => { const button = event.target.closest('[data-action="detail"]'); if (button) openDetail(button.dataset.id, false); });
  $('liste-responsable').addEventListener('click', (event) => { const button = event.target.closest('[data-action]'); if (!button) return; if (button.dataset.action === 'detail') openDetail(button.dataset.id, false); if (button.dataset.action === 'traiter') openDetail(button.dataset.id, true); });
  /* Les boutons de décision sont dans la barre d'actions, sous le formulaire :
     le clic est donc écouté sur la barre, pas sur le formulaire. */
  document.querySelector('.decision-bar').addEventListener('click', (event) => { const button = event.target.closest('[data-decision]'); if (button) decide(button.dataset.decision); });
  $('formulaire-decision').addEventListener('submit', (event) => event.preventDefault());
  document.querySelector('[data-action="retour-traitement"]').addEventListener('click', () => show('vue-responsable'));
  document.querySelectorAll('[data-action="rafraichir"]').forEach((button) => button.addEventListener('click', loadList));
  document.querySelectorAll('[data-filter]').forEach((button) => button.addEventListener('click', () => { state.filter = button.dataset.filter; document.querySelectorAll('[data-filter]').forEach((tab) => tab.classList.toggle('active', tab === button)); renderManagerList(); }));
  $('filtre-demandes').addEventListener('input', renderManagerList);
  $('annee').textContent = String(new Date().getFullYear());
  async function start() {
    try { await Api.appeler('/api/sante'); setHealth('API et base de données disponibles.', true); }
    catch (error) { setHealth('Service indisponible : ' + Messages.expliquer(error).titre, false); }
    try { const response = await Api.appeler('/api/moi'); enter(response.utilisateur); }
    catch (_) { logout(false); }
  }
  start();
})();
