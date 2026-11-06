/**
 * StoryVerse AI — Dashboard Page Controller (dashboard.js)
 * Full Phase 9 implementation:
 *   - Real backend integration via StoryVerseAPI.getProjects()
 *   - Search, filter by type, sort, and pagination
 *   - Real-time portfolio metrics (Total, Stories, Scripts, Characters)
 *   - Version history modal with snapshot previews & restoration
 *   - Safe project deletion with modal confirmation
 *   - Safe DOM construction using textContent (preventing XSS)
 */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements — Metrics
    const statTotalEl = document.getElementById('statTotal');
    const statStoryEl = document.getElementById('statStory');
    const statScriptEl = document.getElementById('statScript');
    const statCharacterEl = document.getElementById('statCharacter');

    // DOM Elements — Toolbar
    const searchInput = document.getElementById('dashboardSearch');
    const clearSearchBtn = document.getElementById('btnClearSearch');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const sortSelect = document.getElementById('sortSelect');

    // DOM Elements — Grid & States
    const projectsGrid = document.getElementById('projectsGrid');
    const emptyState = document.getElementById('dashboardEmptyState');
    const loadingState = document.getElementById('dashboardLoadingState');

    // DOM Elements — Pagination
    const paginationWrap = document.getElementById('dashboardPagination');
    const btnPrevPage = document.getElementById('btnPrevPage');
    const btnNextPage = document.getElementById('btnNextPage');
    const paginationInfo = document.getElementById('paginationInfo');

    // DOM Elements — Version Modal
    const versionModal = document.getElementById('versionModal');
    const versionModalTitle = document.getElementById('versionModalTitle');
    const btnCloseVersionModal = document.getElementById('btnCloseVersionModal');
    const btnCloseVersionModalBtn = document.getElementById('btnCloseVersionModalBtn');
    const versionList = document.getElementById('versionList');
    const versionPreviewPane = document.getElementById('versionPreviewPane');
    const versionPreviewContent = document.getElementById('versionPreviewContent');
    const previewTag = document.getElementById('previewTag');
    const btnRestoreVersion = document.getElementById('btnRestoreVersion');

    // DOM Elements — Delete Modal
    const deleteModal = document.getElementById('deleteModal');
    const deleteProjectTitle = document.getElementById('deleteProjectTitle');
    const btnCloseDeleteModal = document.getElementById('btnCloseDeleteModal');
    const btnCancelDelete = document.getElementById('btnCancelDelete');
    const btnConfirmDelete = document.getElementById('btnConfirmDelete');

    // State
    let currentPage = 1;
    let currentFilter = 'all';
    let currentSearch = '';
    let currentSort = 'updated_at';
    let currentOrder = 'desc';
    let searchDebounceTimer = null;
    let isLoadingProjects = false;

    let activeProjectForVersions = null;
    let selectedVersionId = null;
    let projectToDeleteId = null;

    // ==========================================
    // 1. Data Fetching & Rendering
    // ==========================================
    async function loadProjects() {
      if (isLoadingProjects) return;
      isLoadingProjects = true;

      if (loadingState) loadingState.style.display = 'flex';
      if (projectsGrid) projectsGrid.style.display = 'none';
      if (emptyState) emptyState.style.display = 'none';
      if (paginationWrap) paginationWrap.style.display = 'none';

      try {
        const response = await window.StoryVerseAPI.getProjects({
          search: currentSearch,
          project_type: currentFilter,
          sort_by: currentSort,
          order: currentOrder,
          page: currentPage,
          per_page: 9
        });

        if (response.success && response.data) {
          const { projects, pagination, stats } = response.data;
          updateMetrics(stats);
          renderProjectCards(projects);
          updatePagination(pagination);
        } else {
          throw new Error(response.message || 'Failed to fetch projects.');
        }
      } catch (err) {
        if (window.StoryVerse) {
          const isRateLimit = err.status === 429 || (err.message && err.message.toLowerCase().includes('too many requests'));
          const toastType = isRateLimit ? 'warning' : 'error';
          window.StoryVerse.showToast(err.message || 'Error communicating with server.', toastType);
        }
        if (emptyState) emptyState.style.display = 'block';
      } finally {
        isLoadingProjects = false;
        if (loadingState) loadingState.style.display = 'none';
      }
    }

    function updateMetrics(stats) {
      if (!stats) return;
      if (statTotalEl) statTotalEl.textContent = (stats.total || 0).toLocaleString();
      if (statStoryEl) statStoryEl.textContent = (stats.story || 0).toLocaleString();
      if (statScriptEl) statScriptEl.textContent = (stats.script || 0).toLocaleString();
      if (statCharacterEl) statCharacterEl.textContent = (stats.character || 0).toLocaleString();
    }

    function renderProjectCards(projects) {
      if (!projectsGrid) return;
      projectsGrid.innerHTML = '';

      if (!projects || projects.length === 0) {
        projectsGrid.style.display = 'none';
        if (emptyState) emptyState.style.display = 'block';
        return;
      }

      projectsGrid.style.display = 'grid';
      if (emptyState) emptyState.style.display = 'none';

      projects.forEach(project => {
        const card = createProjectCardElement(project);
        projectsGrid.appendChild(card);
      });
    }

    function createProjectCardElement(project) {
      const card = document.createElement('div');
      card.className = 'project-card';

      // Top area
      const topDiv = document.createElement('div');
      topDiv.className = 'project-card-top';

      // Badges
      const badgesDiv = document.createElement('div');
      badgesDiv.className = 'project-badges';

      const typeBadge = document.createElement('span');
      typeBadge.className = 'badge badge-primary';
      typeBadge.textContent = (project.content_type || 'story').toUpperCase();
      badgesDiv.appendChild(typeBadge);

      if (project.genre) {
        const genreBadge = document.createElement('span');
        genreBadge.className = 'badge badge-secondary';
        genreBadge.textContent = project.genre;
        badgesDiv.appendChild(genreBadge);
      }

      if (project.language && project.language.toLowerCase() !== 'english') {
        const langBadge = document.createElement('span');
        langBadge.className = 'badge badge-secondary';
        langBadge.textContent = project.language;
        badgesDiv.appendChild(langBadge);
      }
      topDiv.appendChild(badgesDiv);

      // Title
      const titleEl = document.createElement('h3');
      titleEl.className = 'project-title';
      titleEl.textContent = project.title || 'Untitled Project';
      topDiv.appendChild(titleEl);

      // Snippet
      const snippetEl = document.createElement('p');
      snippetEl.className = 'project-snippet';
      const snippetContent =
        project.generated_content ||
        project.description ||
        project.topic ||
        'No manuscript content saved yet. Open in workspace to begin drafting.';
      snippetEl.textContent = snippetContent;
      topDiv.appendChild(snippetEl);

      card.appendChild(topDiv);

      // Bottom Meta & Actions
      const metaDiv = document.createElement('div');
      metaDiv.className = 'project-meta';

      const dateEl = document.createElement('span');
      dateEl.textContent = formatRelativeDate(project.updated_at || project.created_at);
      metaDiv.appendChild(dateEl);

      const actionsDiv = document.createElement('div');
      actionsDiv.className = 'project-actions';

      // Version History Button
      const histBtn = document.createElement('button');
      histBtn.className = 'btn btn-secondary btn-sm';
      histBtn.title = 'View version history';
      histBtn.textContent = '📜 Versions';
      histBtn.addEventListener('click', () => openVersionModal(project));
      actionsDiv.appendChild(histBtn);

      // Open in Workspace Button
      const openBtn = document.createElement('a');
      openBtn.className = 'btn btn-primary btn-sm';
      openBtn.href = `editor.html?id=${project.id}`;
      openBtn.textContent = '✏️ Open';
      actionsDiv.appendChild(openBtn);

      // Export Dropdown
      const exportWrap = document.createElement('div');
      exportWrap.className = 'dropdown-wrapper';

      const exportBtn = document.createElement('button');
      exportBtn.className = 'btn btn-secondary btn-sm';
      exportBtn.title = 'Export project (TXT, PDF, DOCX)';
      exportBtn.textContent = '📥 ▾';
      exportWrap.appendChild(exportBtn);

      const exportMenu = document.createElement('div');
      exportMenu.className = 'export-dropdown-menu';
      exportMenu.style.display = 'none';

      const exportOptions = [
        { fmt: 'txt', icon: '📄', label: 'Plain Text (.txt)' },
        { fmt: 'pdf', icon: '📑', label: 'PDF Document (.pdf)' },
        { fmt: 'docx', icon: '📝', label: 'Word Document (.docx)' }
      ];

      exportOptions.forEach(opt => {
        const item = document.createElement('button');
        item.className = 'dropdown-item';
        item.dataset.format = opt.fmt;
        const iconSpan = document.createElement('span');
        iconSpan.textContent = opt.icon;
        item.appendChild(iconSpan);
        item.appendChild(document.createTextNode(' ' + opt.label));

        item.addEventListener('click', async (e) => {
          e.stopPropagation();
          exportMenu.style.display = 'none';
          try {
            if (window.StoryVerse) window.StoryVerse.showToast(`Preparing ${opt.fmt.toUpperCase()} download...`, 'info');
            await window.StoryVerseAPI.exportDocument(opt.fmt, { project_id: project.id });
            if (window.StoryVerse) window.StoryVerse.showToast(`${opt.fmt.toUpperCase()} downloaded successfully!`, 'success');
          } catch (err) {
            if (window.StoryVerse) window.StoryVerse.showToast(err.message || 'Export failed.', 'error');
          }
        });
        exportMenu.appendChild(item);
      });
      exportWrap.appendChild(exportMenu);

      exportBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = exportMenu.style.display === 'flex';
        document.querySelectorAll('.export-dropdown-menu').forEach(m => { m.style.display = 'none'; });
        exportMenu.style.display = isOpen ? 'none' : 'flex';
      });
      document.addEventListener('click', () => { exportMenu.style.display = 'none'; });

      actionsDiv.appendChild(exportWrap);

      // Delete Button
      const delBtn = document.createElement('button');
      delBtn.className = 'btn btn-secondary btn-sm btn-icon-danger';
      delBtn.title = 'Delete project';
      delBtn.textContent = '🗑️';
      delBtn.addEventListener('click', () => openDeleteModal(project));
      actionsDiv.appendChild(delBtn);

      metaDiv.appendChild(actionsDiv);
      card.appendChild(metaDiv);

      return card;
    }

    function updatePagination(pagination) {
      if (!pagination || pagination.total === 0) {
        if (paginationWrap) paginationWrap.style.display = 'none';
        return;
      }

      if (paginationWrap) paginationWrap.style.display = 'flex';
      if (paginationInfo) {
        paginationInfo.textContent = `Page ${pagination.page} of ${pagination.pages} (${pagination.total} projects)`;
      }

      if (btnPrevPage) btnPrevPage.disabled = !pagination.has_prev;
      if (btnNextPage) btnNextPage.disabled = !pagination.has_next;
    }

    function formatRelativeDate(isoStr) {
      if (!isoStr) return 'Recently';
      try {
        const d = new Date(isoStr);
        return d.toLocaleDateString(undefined, {
          month: 'short',
          day: 'numeric',
          year: 'numeric'
        });
      } catch {
        return 'Recently';
      }
    }

    // ==========================================
    // 2. Toolbar Event Listeners
    // ==========================================
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        currentSearch = e.target.value.trim();
        if (clearSearchBtn) {
          clearSearchBtn.style.display = currentSearch ? 'block' : 'none';
        }
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(() => {
          currentPage = 1;
          loadProjects();
        }, 300);
      });
    }

    if (clearSearchBtn) {
      clearSearchBtn.addEventListener('click', () => {
        if (searchInput) searchInput.value = '';
        currentSearch = '';
        clearSearchBtn.style.display = 'none';
        currentPage = 1;
        loadProjects();
      });
    }

    filterButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        if (btn.classList.contains('active')) return; // Avoid duplicate fetch for already active filter
        filterButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.filter || 'all';
        currentPage = 1;
        loadProjects();
      });
    });

    if (sortSelect) {
      sortSelect.addEventListener('change', (e) => {
        const [sortCol, sortDir] = e.target.value.split(':');
        currentSort = sortCol || 'updated_at';
        currentOrder = sortDir || 'desc';
        currentPage = 1;
        loadProjects();
      });
    }

    if (btnPrevPage) {
      btnPrevPage.addEventListener('click', () => {
        if (currentPage > 1) {
          currentPage--;
          loadProjects();
        }
      });
    }

    if (btnNextPage) {
      btnNextPage.addEventListener('click', () => {
        currentPage++;
        loadProjects();
      });
    }

    // ==========================================
    // 3. Version History Modal Handlers
    // ==========================================
    async function openVersionModal(project) {
      activeProjectForVersions = project;
      selectedVersionId = null;

      if (versionModalTitle) {
        versionModalTitle.textContent = `Version History: "${project.title}"`;
      }
      if (versionPreviewPane) versionPreviewPane.style.display = 'none';
      if (versionList) versionList.innerHTML = '<p style="color:var(--text-muted);font-size:0.85rem;">Loading versions...</p>';

      if (versionModal) versionModal.style.display = 'flex';

      try {
        const res = await window.StoryVerseAPI.getProjectVersions(project.id, 'desc');
        if (res.success && res.data) {
          renderVersionItems(res.data);
        } else {
          throw new Error(res.message || 'Could not load version history.');
        }
      } catch (err) {
        if (versionList) {
          versionList.innerHTML = '';
          const errP = document.createElement('p');
          errP.style.color = '#ef4444';
          errP.style.fontSize = '0.85rem';
          errP.textContent = `Error: ${err.message}`;
          versionList.appendChild(errP);
        }
      }
    }

    function renderVersionItems(versions) {
      if (!versionList) return;
      versionList.innerHTML = '';

      if (!versions || versions.length === 0) {
        versionList.innerHTML = '<p style="color:var(--text-muted);font-size:0.85rem;">No previous versions recorded for this project.</p>';
        return;
      }

      versions.forEach((v, idx) => {
        const item = document.createElement('div');
        item.className = 'version-item';

        const metaDiv = document.createElement('div');
        metaDiv.className = 'version-meta';

        const numSpan = document.createElement('span');
        numSpan.className = 'version-num';
        numSpan.textContent = `Snapshot #${versions.length - idx} • ${v.operation || 'Saved Version'}`;
        metaDiv.appendChild(numSpan);

        const dateSpan = document.createElement('span');
        dateSpan.className = 'version-date';
        dateSpan.textContent = `${formatRelativeDate(v.created_at)} — ${v.input_summary || 'No description'}`;
        metaDiv.appendChild(dateSpan);

        item.appendChild(metaDiv);

        const viewSpan = document.createElement('span');
        viewSpan.className = 'btn btn-secondary btn-sm';
        viewSpan.textContent = 'Preview';
        item.appendChild(viewSpan);

        item.addEventListener('click', () => {
          document.querySelectorAll('.version-item').forEach(el => el.classList.remove('active'));
          item.classList.add('active');
          showVersionPreview(v);
        });

        versionList.appendChild(item);
      });
    }

    function showVersionPreview(version) {
      selectedVersionId = version.id;
      if (!versionPreviewPane || !versionPreviewContent) return;

      if (previewTag) {
        previewTag.textContent = `Version #${version.id} (${version.operation || 'Snapshot'})`;
      }
      versionPreviewContent.textContent = version.content_snapshot || '(Empty snapshot)';
      versionPreviewPane.style.display = 'block';
    }

    if (btnRestoreVersion) {
      btnRestoreVersion.addEventListener('click', async () => {
        if (!activeProjectForVersions || !selectedVersionId) return;
        if (!confirm('Are you sure you want to restore this past snapshot? It will update the active manuscript.')) {
          return;
        }

        try {
          btnRestoreVersion.disabled = true;
          const res = await window.StoryVerseAPI.restoreProjectVersion(activeProjectForVersions.id, selectedVersionId);
          if (res.success) {
            if (window.StoryVerse) {
              window.StoryVerse.showToast('Project restored successfully.', 'success');
            }
            closeVersionModal();
            loadProjects();
          } else {
            throw new Error(res.message || 'Restore failed.');
          }
        } catch (err) {
          if (window.StoryVerse) {
            window.StoryVerse.showToast(err.message || 'Error restoring version.', 'error');
          }
        } finally {
          btnRestoreVersion.disabled = false;
        }
      });
    }

    function closeVersionModal() {
      if (versionModal) versionModal.style.display = 'none';
      activeProjectForVersions = null;
      selectedVersionId = null;
    }

    if (btnCloseVersionModal) btnCloseVersionModal.addEventListener('click', closeVersionModal);
    if (btnCloseVersionModalBtn) btnCloseVersionModalBtn.addEventListener('click', closeVersionModal);

    // ==========================================
    // 4. Project Deletion Modal Handlers
    // ==========================================
    function openDeleteModal(project) {
      projectToDeleteId = project.id;
      if (deleteProjectTitle) deleteProjectTitle.textContent = `"${project.title}"`;
      if (deleteModal) deleteModal.style.display = 'flex';
    }

    function closeDeleteModal() {
      if (deleteModal) deleteModal.style.display = 'none';
      projectToDeleteId = null;
    }

    if (btnCloseDeleteModal) btnCloseDeleteModal.addEventListener('click', closeDeleteModal);
    if (btnCancelDelete) btnCancelDelete.addEventListener('click', closeDeleteModal);

    if (btnConfirmDelete) {
      btnConfirmDelete.addEventListener('click', async () => {
        if (!projectToDeleteId) return;

        try {
          btnConfirmDelete.disabled = true;
          const res = await window.StoryVerseAPI.deleteProject(projectToDeleteId);
          if (res.success) {
            if (window.StoryVerse) {
              window.StoryVerse.showToast('Project deleted successfully.', 'info');
            }
            closeDeleteModal();
            loadProjects();
          } else {
            throw new Error(res.message || 'Deletion failed.');
          }
        } catch (err) {
          if (window.StoryVerse) {
            window.StoryVerse.showToast(err.message || 'Failed to delete project.', 'error');
          }
        } finally {
          btnConfirmDelete.disabled = false;
        }
      });
    }

    // Initial Load
    loadProjects();
  });
})();
