/**
 * StoryVerse AI — Screenplay / Script Page Logic (script.js)
 * ============================================================
 * Phase 6: Screenplay generation, real-time parameter tracking,
 * industry-standard screenplay formatting, scene breakdown cards,
 * editable manuscript, and clipboard copying.
 */

(function () {
  'use strict';

  // State
  let currentScriptData = null;
  let currentScriptParameters = null;
  let savedProjectId = null;
  let lastSavedContent = null;
  let isSavingProject = false;

  document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const form = document.getElementById('scriptForm');
    if (!form) return;

    const topicInput = document.getElementById('scriptTopic');
    const genreInput = document.getElementById('scriptGenre');
    const languageInput = document.getElementById('scriptLanguage');
    const scenesInput = document.getElementById('numScenes');
    const toneInput = document.getElementById('scriptTone');
    const charsInput = document.getElementById('scriptCharacters');
    const settingInput = document.getElementById('scriptSetting');
    const instructionsInput = document.getElementById('scriptInstructions');
    const generateBtn = document.getElementById('generateScriptBtn');
    const charCounter = document.getElementById('scriptCharCount');

    // Sidebar Summary Elements
    const summaryGenre = document.getElementById('summaryScriptGenre');
    const summaryLang = document.getElementById('summaryScriptLanguage');
    const summaryScenes = document.getElementById('summaryScriptScenes');
    const summaryTone = document.getElementById('summaryScriptTone');

    // Loading & Result Section Elements
    const loadingState = document.getElementById('scriptLoadingState');
    const resultSection = document.getElementById('scriptResultSection');

    // Result Header Elements
    const resultTitle = document.getElementById('resultScriptTitle');
    const badgeGenre = document.getElementById('resultGenreBadge');
    const badgeLang = document.getElementById('resultLanguageBadge');
    const badgeScenes = document.getElementById('resultScenesBadge');
    const badgeTone = document.getElementById('resultToneBadge');
    const loglineBox = document.getElementById('resultScriptLoglineBox');
    const loglineText = document.getElementById('resultScriptLogline');
    const charsBox = document.getElementById('resultScriptCharactersBox');
    const charsText = document.getElementById('resultScriptCharacters');

    // View Containers & Toggle Buttons
    const viewScreenplayBtn = document.getElementById('viewScreenplayBtn');
    const viewSceneCardsBtn = document.getElementById('viewSceneCardsBtn');
    const viewEditableBtn = document.getElementById('viewEditableBtn');
    const screenplayView = document.getElementById('screenplayView');
    const screenplayContent = document.getElementById('screenplayContent');
    const sceneCardsView = document.getElementById('sceneCardsView');
    const editableView = document.getElementById('editableView');
    const editableTextarea = document.getElementById('scriptEditableText');

    // Action Toolbar Buttons
    const copyBtn = document.getElementById('scriptCopyBtn');
    const regenerateBtn = document.getElementById('scriptRegenerateBtn');
    const addSceneBtn = document.getElementById('scriptGenerateSceneBtn');

    // ============================================================
    // 1. Live Summary & Character Counter
    // ============================================================
    function updateCharCounter() {
      if (topicInput && charCounter) {
        charCounter.textContent = `${topicInput.value.length} / 2000`;
      }
    }

    function updateSummary() {
      if (genreInput && summaryGenre) summaryGenre.textContent = genreInput.value;
      if (languageInput && summaryLang) summaryLang.textContent = languageInput.value;
      if (scenesInput && summaryScenes) summaryScenes.textContent = `${scenesInput.value} Scenes`;
      if (toneInput && summaryTone) summaryTone.textContent = toneInput.value;
    }

    if (topicInput) topicInput.addEventListener('input', updateCharCounter);
    if (genreInput) genreInput.addEventListener('change', updateSummary);
    if (languageInput) languageInput.addEventListener('change', updateSummary);
    if (scenesInput) scenesInput.addEventListener('input', updateSummary);
    if (toneInput) toneInput.addEventListener('change', updateSummary);

    // Initial update
    updateCharCounter();
    updateSummary();

    // ============================================================
    // 2. View Mode Switcher
    // ============================================================
    function switchView(mode) {
      // Toggle button active classes
      if (viewScreenplayBtn) viewScreenplayBtn.classList.toggle('active', mode === 'screenplay');
      if (viewSceneCardsBtn) viewSceneCardsBtn.classList.toggle('active', mode === 'cards');
      if (viewEditableBtn) viewEditableBtn.classList.toggle('active', mode === 'editable');

      // Toggle container visibility
      if (screenplayView) screenplayView.style.display = mode === 'screenplay' ? 'flex' : 'none';
      if (sceneCardsView) sceneCardsView.style.display = mode === 'cards' ? 'flex' : 'none';
      if (editableView) editableView.style.display = mode === 'editable' ? 'block' : 'none';
    }

    if (viewScreenplayBtn) viewScreenplayBtn.addEventListener('click', () => switchView('screenplay'));
    if (viewSceneCardsBtn) viewSceneCardsBtn.addEventListener('click', () => switchView('cards'));
    if (viewEditableBtn) viewEditableBtn.addEventListener('click', () => switchView('editable'));

    // ============================================================
    // 3. Form Submission — Generate Screenplay
    // ============================================================
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const topic = topicInput ? topicInput.value.trim() : '';
      if (!topic) {
        if (window.StoryVerse) window.StoryVerse.showToast('Please enter a screenplay premise or logline.', 'warning');
        if (topicInput) topicInput.focus();
        return;
      }

      const numScenesVal = parseInt(scenesInput ? scenesInput.value : '3', 10);
      if (isNaN(numScenesVal) || numScenesVal < 1 || numScenesVal > 20) {
        if (window.StoryVerse) window.StoryVerse.showToast('Number of scenes must be between 1 and 20.', 'warning');
        return;
      }

      // Collect payload
      const payload = {
        topic: topic,
        genre: genreInput ? genreInput.value : 'Thriller',
        language: languageInput ? languageInput.value : 'English',
        num_scenes: numScenesVal,
        tone: toneInput ? toneInput.value : 'Suspenseful',
        characters: charsInput && charsInput.value.trim() ? charsInput.value.trim() : null,
        setting: settingInput && settingInput.value.trim() ? settingInput.value.trim() : null,
        additional_instructions: instructionsInput && instructionsInput.value.trim() ? instructionsInput.value.trim() : null
      };

      // Set Loading State
      if (resultSection) resultSection.style.display = 'none';
      if (loadingState) {
        loadingState.style.display = 'block';
        loadingState.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      if (generateBtn) {
        generateBtn.disabled = true;
        const textSpan = generateBtn.querySelector('.btn-text');
        if (textSpan) textSpan.textContent = 'Generating Screenplay...';
      }

      try {
        const response = await window.StoryVerseAPI.generateScript(payload);

        if (response && response.success && response.data) {
          currentScriptData = response.data;
          currentScriptParameters = payload;
          savedProjectId = null;
          lastSavedContent = null;
          renderScreenplayResult(response.data);
          if (window.StoryVerse) {
            window.StoryVerse.showToast('🎬 Screenplay generated successfully!', 'success');
          }
        } else {
          const errMsg = response?.message || 'Failed to generate screenplay. Please try again.';
          if (window.StoryVerse) window.StoryVerse.showToast(errMsg, 'error');
        }
      } catch (err) {
        console.error('Screenplay generation failed:', err);
        const userMsg = err.message || 'Error communicating with AI service.';
        if (window.StoryVerse) window.StoryVerse.showToast(userMsg, 'error');
      } finally {
        if (loadingState) loadingState.style.display = 'none';
        if (generateBtn) {
          generateBtn.disabled = false;
          const textSpan = generateBtn.querySelector('.btn-text');
          if (textSpan) textSpan.textContent = '🎬 Generate Screenplay';
        }
      }
    });

    // ============================================================
    // 4. Render Screenplay Results (Safe DOM Rendering)
    // ============================================================
    function renderScreenplayResult(data) {
      if (!data) return;

      // Title & Badges
      if (resultTitle) resultTitle.textContent = data.title || 'Untitled Screenplay';
      if (badgeGenre) badgeGenre.textContent = data.metadata?.genre || 'Screenplay';
      if (badgeLang) badgeLang.textContent = data.metadata?.language || 'English';
      if (badgeScenes) badgeScenes.textContent = `${data.scene_count || data.scenes?.length || 1} Scenes`;
      if (badgeTone) badgeTone.textContent = data.metadata?.tone || 'Cinematic';

      // Logline Box
      if (loglineBox && loglineText) {
        if (data.logline) {
          loglineText.textContent = data.logline;
          loglineBox.style.display = 'flex';
        } else {
          loglineBox.style.display = 'none';
        }
      }

      // Characters Box
      if (charsBox && charsText) {
        if (data.characters_summary) {
          charsText.textContent = data.characters_summary;
          charsBox.style.display = 'flex';
        } else {
          charsBox.style.display = 'none';
        }
      }

      // 1. Render Courier Screenplay Page
      renderCourierPage(data);

      // 2. Render Scene Breakdown Cards
      renderSceneCards(data);

      // 3. Render Editable Textarea
      if (editableTextarea) {
        editableTextarea.value = data.full_script || '';
      }

      // Show Result Section and switch to screenplay view
      switchView('screenplay');
      if (resultSection) {
        resultSection.style.display = 'block';
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    /**
     * Builds standard Hollywood screenplay DOM nodes using safe textContent.
     */
    function renderCourierPage(data) {
      if (!screenplayContent) return;
      screenplayContent.replaceChildren(); // Clear existing safely

      const scenes = data.scenes || [];
      if (scenes.length === 0) {
        const fallbackP = document.createElement('p');
        fallbackP.textContent = data.full_script || 'No screenplay scenes generated.';
        screenplayContent.appendChild(fallbackP);
        return;
      }

      scenes.forEach((scene) => {
        const sceneBlock = document.createElement('div');
        sceneBlock.className = 'sp-scene-block';

        // Slugline (e.g. INT. SUBWAY - NIGHT)
        const slugP = document.createElement('div');
        slugP.className = 'sp-slugline';
        slugP.textContent = scene.heading || `SCENE ${scene.scene_number}`;
        sceneBlock.appendChild(slugP);

        // Action block
        if (scene.action) {
          const actionP = document.createElement('div');
          actionP.className = 'sp-action';
          actionP.textContent = scene.action;
          sceneBlock.appendChild(actionP);
        }

        // Dialogues
        if (Array.isArray(scene.dialogues) && scene.dialogues.length > 0) {
          scene.dialogues.forEach((d) => {
            const dUnit = document.createElement('div');
            dUnit.className = 'sp-dialogue-unit';

            // Character Cue (Centered/Capitalized)
            const charCue = document.createElement('div');
            charCue.className = 'sp-char-cue';
            charCue.textContent = (d.character || 'CHARACTER').toUpperCase();
            dUnit.appendChild(charCue);

            // Parenthetical (if present)
            if (d.parenthetical) {
              const parenthetical = document.createElement('div');
              parenthetical.className = 'sp-parenthetical';
              parenthetical.textContent = d.parenthetical;
              dUnit.appendChild(parenthetical);
            }

            // Dialogue Line
            const dialogueLine = document.createElement('div');
            dialogueLine.className = 'sp-dialogue';
            dialogueLine.textContent = d.line || '';
            dUnit.appendChild(dialogueLine);

            sceneBlock.appendChild(dUnit);
          });
        }

        // Transition (e.g. CUT TO:)
        if (scene.transition) {
          const transP = document.createElement('div');
          transP.className = 'sp-transition';
          transP.textContent = scene.transition;
          sceneBlock.appendChild(transP);
        }

        screenplayContent.appendChild(sceneBlock);
      });
    }

    /**
     * Builds Scene Breakdown Cards DOM nodes.
     */
    function renderSceneCards(data) {
      if (!sceneCardsView) return;
      sceneCardsView.replaceChildren(); // Clear existing safely

      const scenes = data.scenes || [];
      if (scenes.length === 0) {
        const emptyMsg = document.createElement('p');
        emptyMsg.textContent = 'No scenes to display in card view.';
        sceneCardsView.appendChild(emptyMsg);
        return;
      }

      scenes.forEach((scene) => {
        const card = document.createElement('div');
        card.className = 'scene-breakdown-card';

        // Header
        const header = document.createElement('div');
        header.className = 'scene-card-header';

        const badge = document.createElement('span');
        badge.className = 'scene-badge-pill';
        badge.textContent = `SCENE ${scene.scene_number || 1}`;
        header.appendChild(badge);

        const heading = document.createElement('span');
        heading.className = 'scene-heading-title';
        heading.textContent = scene.heading || 'Scene Heading';
        header.appendChild(heading);

        card.appendChild(header);

        // Action Summary
        if (scene.action) {
          const actionText = document.createElement('div');
          actionText.className = 'scene-action-summary';
          actionText.textContent = scene.action;
          card.appendChild(actionText);
        }

        // Dialogues Preview
        if (Array.isArray(scene.dialogues) && scene.dialogues.length > 0) {
          const dList = document.createElement('div');
          dList.className = 'scene-dialogues-list';

          const dCount = document.createElement('div');
          dCount.className = 'scene-dialogues-count';
          dCount.textContent = `Dialogues (${scene.dialogues.length} exchanges)`;
          dList.appendChild(dCount);

          scene.dialogues.slice(0, 3).forEach((d) => {
            const item = document.createElement('div');
            item.className = 'dialogue-preview-item';

            const charSpan = document.createElement('span');
            charSpan.className = 'dialogue-preview-char';
            charSpan.textContent = `${d.character}: `;
            item.appendChild(charSpan);

            const lineSpan = document.createElement('span');
            lineSpan.textContent = d.line;
            item.appendChild(lineSpan);

            dList.appendChild(item);
          });

          if (scene.dialogues.length > 3) {
            const moreSpan = document.createElement('div');
            moreSpan.style.fontSize = '0.8rem';
            moreSpan.style.color = 'var(--text-muted)';
            moreSpan.style.marginTop = '0.35rem';
            moreSpan.textContent = `+ ${scene.dialogues.length - 3} more lines in full script`;
            dList.appendChild(moreSpan);
          }

          card.appendChild(dList);
        }

        sceneCardsView.appendChild(card);
      });
    }

    // ============================================================
    // 5. Action Toolbar Handlers
    // ============================================================

    // Copy to Clipboard
    if (copyBtn) {
      copyBtn.addEventListener('click', async () => {
        const textToCopy = editableTextarea && editableTextarea.value.trim()
          ? editableTextarea.value.trim()
          : (currentScriptData?.full_script || '');

        if (!textToCopy) {
          if (window.StoryVerse) window.StoryVerse.showToast('No screenplay text to copy.', 'warning');
          return;
        }

        try {
          await navigator.clipboard.writeText(textToCopy);
          if (window.StoryVerse) window.StoryVerse.showToast('📋 Screenplay copied to clipboard!', 'success');
        } catch (err) {
          // Fallback selection copy
          if (editableTextarea) {
            editableTextarea.select();
            document.execCommand('copy');
            if (window.StoryVerse) window.StoryVerse.showToast('📋 Screenplay copied!', 'success');
          }
        }
      });
    }

    // Regenerate
    if (regenerateBtn) {
      regenerateBtn.addEventListener('click', () => {
        if (form) {
          form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        }
      });
    }

    // Add Scene
    if (addSceneBtn) {
      addSceneBtn.addEventListener('click', async () => {
        if (!currentScriptData) return;

        const sceneGoal = prompt('What happens in the next scene? (Brief dramatic goal):');
        if (!sceneGoal || !sceneGoal.trim()) return;

        const nextSceneNum = (currentScriptData.scenes?.length || 0) + 1;
        const lastScene = currentScriptData.scenes?.[currentScriptData.scenes.length - 1];
        const lastHeading = lastScene ? lastScene.heading : 'Previous scene';

        // Show brief toast
        if (window.StoryVerse) window.StoryVerse.showToast(`Drafting Scene ${nextSceneNum}...`, 'info');

        try {
          const res = await window.StoryVerseAPI.generateScene({
            scene_goal: sceneGoal.trim(),
            context: `Context from ${lastHeading}:\n${lastScene?.action || ''}`,
            genre: currentScriptData.metadata?.genre || 'Thriller',
            language: currentScriptData.metadata?.language || 'English'
          });

          if (res && res.success && res.data) {
            const newScene = res.data.scene;
            newScene.scene_number = nextSceneNum;
            currentScriptData.scenes.push(newScene);
            currentScriptData.full_script += `\n\nSCENE ${nextSceneNum}\n${res.data.full_text}`;

            // Re-render
            renderScreenplayResult(currentScriptData);
            if (window.StoryVerse) window.StoryVerse.showToast(`🎬 Scene ${nextSceneNum} added successfully!`, 'success');
          } else {
            if (window.StoryVerse) window.StoryVerse.showToast(res?.message || 'Failed to add scene.', 'error');
          }
        } catch (err) {
          if (window.StoryVerse) window.StoryVerse.showToast('Error generating next scene.', 'error');
        }
      });
    }

    // Save as Project
    const saveProjectBtn = document.getElementById('scriptSaveProjectBtn');
    if (saveProjectBtn) {
      saveProjectBtn.addEventListener('click', async () => {
        if (isSavingProject) return;
        if (!currentScriptData) {
          if (window.StoryVerse) window.StoryVerse.showToast('No script generated yet to save.', 'warning');
          return;
        }

        const title = currentScriptData.title || 'Screenplay Project';
        const content = editableTextarea ? editableTextarea.value : (currentScriptData.full_script || '');
        if (!content.trim()) {
          if (window.StoryVerse) window.StoryVerse.showToast('The screenplay has no content to save.', 'warning');
          return;
        }

        if (savedProjectId && content === lastSavedContent) {
          if (window.StoryVerse) window.StoryVerse.showToast(`This screenplay is already saved as project #${savedProjectId}.`, 'info');
          return;
        }

        const metadata = currentScriptData.metadata || {};
        const generationParameters = {
          ...(currentScriptParameters || {}),
          topic: currentScriptParameters?.topic || metadata.topic || '',
          genre: metadata.genre || currentScriptParameters?.genre || 'Thriller',
          language: metadata.language || currentScriptParameters?.language || 'English',
          tone: metadata.tone || currentScriptParameters?.tone || 'Suspenseful',
          requested_scenes: metadata.requested_scenes || currentScriptParameters?.num_scenes || currentScriptData.scene_count,
          detected_scenes: currentScriptData.scene_count || currentScriptData.scenes?.length || 0,
          characters_summary: currentScriptData.characters_summary || '',
          logline: currentScriptData.logline || ''
        };
        const inputSummary = [
          `Topic: ${generationParameters.topic}`,
          `Genre: ${generationParameters.genre}`,
          `Language: ${generationParameters.language}`,
          `Tone: ${generationParameters.tone}`,
          `Scenes: ${generationParameters.requested_scenes}`
        ].join(', ').slice(0, 500);

        const isUpdatingProject = savedProjectId !== null;
        isSavingProject = true;
        saveProjectBtn.disabled = true;
        const originalButtonText = saveProjectBtn.textContent;
        saveProjectBtn.textContent = isUpdatingProject ? 'Saving Changes...' : 'Saving...';
        try {
          let res;
          if (isUpdatingProject) {
            res = await window.StoryVerseAPI.updateProject(savedProjectId, {
              title,
              content_type: 'script',
              genre: generationParameters.genre,
              language: generationParameters.language,
              tone: generationParameters.tone,
              topic: generationParameters.topic,
              description: generationParameters.logline || generationParameters.topic,
              content
            });
          } else {
            res = await window.StoryVerseAPI.createProject({
              title,
              content_type: 'script',
              genre: generationParameters.genre,
              language: generationParameters.language,
              tone: generationParameters.tone,
              topic: generationParameters.topic,
              description: generationParameters.logline || generationParameters.topic,
              content,
              input_summary: inputSummary,
              generation_parameters: generationParameters,
              ai_model: metadata.model || metadata.provider || 'Gemini',
              tokens_used: metadata.tokens_used
            });
          }

          if (!res?.success || !res.data || res.data.id == null) {
            throw new Error(res?.message || 'The server did not confirm that the screenplay was saved.');
          }

          savedProjectId = res.data.id;
          lastSavedContent = content;
          if (window.StoryVerse) {
            const action = res.message || (isUpdatingProject ? 'Screenplay updated successfully.' : 'Screenplay saved successfully.');
            window.StoryVerse.showToast(`${action} Project #${savedProjectId}`, 'success');
          }
        } catch (err) {
          console.error('Screenplay save failed:', err);
          if (window.StoryVerse) {
            window.StoryVerse.showToast(err.message || 'Could not save the screenplay. Please try again.', 'error');
          }
        } finally {
          isSavingProject = false;
          saveProjectBtn.disabled = false;
          saveProjectBtn.textContent = originalButtonText;
        }
      });
    }

    // Export dropdown toggle + per-format download
    const scriptExportBtn = document.getElementById('scriptExportBtn');
    const scriptExportMenu = document.getElementById('scriptExportMenu');
    if (scriptExportBtn && scriptExportMenu) {
      scriptExportBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        scriptExportMenu.style.display = scriptExportMenu.style.display === 'none' ? 'flex' : 'none';
      });
      document.addEventListener('click', () => { scriptExportMenu.style.display = 'none'; });

      scriptExportMenu.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', async () => {
          const format = item.dataset.format;
          scriptExportMenu.style.display = 'none';
          const title = (currentScriptData && currentScriptData.title) || document.getElementById('resultScriptTitle')?.textContent.trim() || 'Screenplay';
          const content = editableTextarea && editableTextarea.value.trim() ? editableTextarea.value.trim() : (currentScriptData?.full_script || '');
          if (!content) {
            if (window.StoryVerse) window.StoryVerse.showToast('No script content to export.', 'warning');
            return;
          }
          item.disabled = true;
          try {
            if (window.StoryVerse) window.StoryVerse.showToast(`Preparing ${format.toUpperCase()} download...`, 'info');
            await window.StoryVerseAPI.exportDocument(format, {
              title: title,
              content: content,
              project_type: 'script',
              genre: (currentScriptData && currentScriptData.metadata?.genre) || (genreInput ? genreInput.value : undefined),
              language: (currentScriptData && currentScriptData.metadata?.language) || (languageInput ? languageInput.value : 'English')
            });
            if (window.StoryVerse) window.StoryVerse.showToast(`${format.toUpperCase()} downloaded successfully!`, 'success');
          } catch (err) {
            if (window.StoryVerse) window.StoryVerse.showToast(err.message || 'Export failed.', 'error');
          } finally {
            item.disabled = false;
          }
        });
      });
    }
  });
})();
