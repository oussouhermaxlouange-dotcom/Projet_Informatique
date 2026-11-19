/* Valeurs d'API rendues uniquement comme texte. */
(function (global) {
  'use strict';
  const LIBELLES = { BROUILLON: 'Brouillon', SOUMISE: 'En attente', VALIDEE: 'Validée', REFUSEE: 'Refusée' };
  const ORDRE = ['VALIDEE', 'SOUMISE', 'REFUSEE', 'BROUILLON'];

  function date(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}/.test(value)) return '—';
    const [year, month, day] = value.slice(0, 10).split('-');
    return day + '/' + month + '/' + year;
  }
  function period(item) { return date(item.date_debut) + ' – ' + date(item.date_fin); }
  function text(node, value) { node.textContent = value === null || value === undefined || value === '' ? '—' : String(value); }
  function badge(status) {
    const node = document.createElement('span');
    node.className = 'status-tag status-' + String(status || '').toLowerCase();
    text(node, LIBELLES[status] || status || 'Inconnu');
    return node;
  }
  function cell(value) { const td = document.createElement('td'); text(td, value); return td; }
  function action(label, actionName, id, className) {
    const button = document.createElement('button');
    button.type = 'button'; button.className = className; button.dataset.action = actionName; button.dataset.id = String(id); button.textContent = label;
    return button;
  }
  function studentRows(body, items) {
    body.replaceChildren();
    (items || []).forEach(function (item) {
      const row = document.createElement('tr');
      const title = document.createElement('td'); const strong = document.createElement('strong'); text(strong, item.intitule); title.append(strong);
      const company = cell(item.entreprise);
      const periodCell = cell(period(item)); periodCell.className = 'nowrap';
      const statusCell = document.createElement('td'); statusCell.append(badge(item.statut));
      const actionCell = document.createElement('td'); actionCell.append(action('Consulter', 'detail', item.id, 'link-button'));
      row.append(title, company, periodCell, statusCell, actionCell); body.append(row);
    });
  }
  function managerCards(container, items, canDecide, filter, query) {
    container.replaceChildren();
    const normalized = String(query || '').trim().toLocaleLowerCase('fr');
    (items || []).filter(function (item) {
      return (filter === 'all' || item.statut === filter) && (!normalized || [item.etudiant, item.entreprise, item.intitule].some(function (value) { return String(value || '').toLocaleLowerCase('fr').includes(normalized); }));
    }).forEach(function (item) {
      const card = document.createElement('article'); card.className = 'request-card';
      const main = document.createElement('div'); main.className = 'request-main';
      const name = document.createElement('h2'); text(name, item.etudiant);
      const reference = document.createElement('p'); reference.className = 'muted small'; text(reference, 'Convention n° ' + item.id);
      const subline = document.createElement('p'); subline.className = 'request-title'; text(subline, item.intitule);
      main.append(name, reference, subline);
      const company = document.createElement('div'); company.className = 'request-meta';
      const companyLabel = document.createElement('span'); companyLabel.className = 'data-label'; companyLabel.textContent = 'Entreprise d’accueil';
      const companyValue = document.createElement('strong'); text(companyValue, item.entreprise);
      company.append(companyLabel, companyValue);
      const dates = document.createElement('div'); dates.className = 'request-meta';
      const datesLabel = document.createElement('span'); datesLabel.className = 'data-label'; datesLabel.textContent = 'Période de stage';
      const datesValue = document.createElement('strong'); text(datesValue, period(item)); dates.append(datesLabel, datesValue);
      const status = document.createElement('div'); status.append(badge(item.statut));
      const actions = document.createElement('div'); actions.className = 'request-actions';
      if (item.statut === 'SOUMISE' && canDecide) actions.append(action('Décider', 'traiter', item.id, 'button button-dark button-small'));
      else actions.append(action('Consulter', 'detail', item.id, 'button button-light button-small'));
      card.append(main, company, dates, status, actions); container.append(card);
    });
  }
  function statistics(container, items) {
    container.replaceChildren();
    const labels = { VALIDEE: 'Validées', SOUMISE: 'En cours de revue', REFUSEE: 'Rejetées', BROUILLON: 'Brouillons' };
    ORDRE.slice(0, 3).forEach(function (status) {
      const count = (items || []).filter(function (item) { return item.statut === status; }).length;
      const card = document.createElement('div'); card.className = 'summary-card';
      const label = document.createElement('span'); label.className = 'data-label'; label.textContent = labels[status];
      const number = document.createElement('strong'); number.textContent = String(count);
      card.append(label, number); container.append(card);
    });
  }
  global.Rendu = { libelles: LIBELLES, date: date, periode: period, badge: badge, lignesEtudiant: studentRows, cartesResponsable: managerCards, statistiques: statistics };
})(window);
