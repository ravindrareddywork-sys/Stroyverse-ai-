/**
 * StoryVerse AI — Workspace Editor Page Logic (editor.js)
 * Full Phase 8 implementation: Real-time stats, AI writing assistant tools
 * (Rewrite, Translate, Summarize, Dialogue, Plot Twist, Continue),
 * side-by-side comparison view, copy, append, and replacement workflows.
 */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements — Writing Area
    const textarea = document.getElementById('editorTextarea');
    const wordCountEl = document.getElementById('wordCount');
    const charCountEl = document.getElementById('charCount');
    const readingTimeEl = document.getElementById('readingTime');
    const selectionStatusEl = document.getElementById('selectionStatus');
    const titleInput = document.getElementById('editorTitle');
    const saveBtn = document.getElementById('saveProjectBtn');
    const exportBtn = document.getElementById('exportDropdownBtn');
    const sampleBtn = document.getElementById('btnSampleText');
    const clearBtn = document.getElementById('btnClearText');
    const copyEditorBtn = document.getElementById('btnCopyEditorText');

    // DOM Elements — AI Result Card & Views
    const aiResultCard = document.getElementById('aiResultCard');
    const resultIcon = document.getElementById('resultIcon');
    const resultHeading = document.getElementById('resultHeading');
    const badgeOperation = document.getElementById('badgeOperation');
    const badgeModel = document.getElementById('badgeModel');
    const btnReplaceText = document.getElementById('btnReplaceText');
    const btnAppendText = document.getElementById('btnAppendText');
    const btnCopyResult = document.getElementById('btnCopyResult');
    const btnDismissResult = document.getElementById('btnDismissResult');
    const viewSingleOutput = document.getElementById('viewSingleOutput');
    const viewComparison = document.getElementById('viewComparison');
    const resultOutputText = document.getElementById('resultOutputText');
    const comparisonOriginalText = document.getElementById('comparisonOriginalText');
    const comparisonGeneratedText = document.getElementById('comparisonGeneratedText');
    const viewTabBtns = document.querySelectorAll('.view-tab-btn');

    // DOM Elements — Assistant Sidebar & Tools
    const toolPills = document.querySelectorAll('.tool-pill');
    const toolFormPanels = document.querySelectorAll('.tool-form-panel');
    const assistantLoading = document.getElementById('assistantLoading');
    const assistantLoadingText = document.getElementById('assistantLoadingText');

    // Tool Action Buttons
    const btnExecuteRewrite = document.getElementById('btnExecuteRewrite');
    const btnExecuteTranslate = document.getElementById('btnExecuteTranslate');
    const btnExecuteSummarize = document.getElementById('btnExecuteSummarize');
    const btnExecuteDialogue = document.getElementById('btnExecuteDialogue');
    const btnExecuteTwist = document.getElementById('btnExecuteTwist');
    const btnExecuteContinue = document.getElementById('btnExecuteContinue');

    // State
    let activeProjectId = null;
    let lastSavedContent = '';
    let currentResult = {
      operation: '',
      originalText: '',
      generatedText: '',
      isSelection: false,
      selectionStart: 0,
      selectionEnd: 0
    };

    const SAMPLE_SCENE = `Dr. Evelyn Ross adjusted the frequency dials of the radio telescope atop the Atacama plateau, noticing an inexplicable pulse rhythmic as a heartbeat. The signal originated not from any cataloged satellite constellation, but from the void between Cygnus and Lyra.

Behind her, the cooling fans of the supercomputing array hummed a steady monotone. Her graduate student, Arjun, rubbed his exhausted eyes and leaned over the phosphor-green spectrogram.

"Doctor," Arjun murmured, his voice tightening. "The pulse isn't random noise. It's a binary prime sequence repeating every 11.4 seconds."`;

    // ==========================================
    // 1. Textarea Statistics & Selection Tracking
    // ==========================================
    function updateStats() {
      if (!textarea) return;
      const text = textarea.value.trim();
      const words = text === '' ? 0 : text.split(/\s+/).length;
      const chars = textarea.value.length;
      const readingMinutes = Math.max(1, Math.ceil(words / 200));

      if (wordCountEl) wordCountEl.textContent = `${words.toLocaleString()} words`;
      if (charCountEl) charCountEl.textContent = `${chars.toLocaleString()} characters`;
      if (readingTimeEl) readingTimeEl.textContent = `~${readingMinutes} min read`;

      updateSelectionStatus();
    }

    function updateSelectionStatus() {
      if (!textarea || !selectionStatusEl) return;
      const selStart = textarea.selectionStart;
      const selEnd = textarea.selectionEnd;
      const selected = textarea.value.substring(selStart, selEnd).trim();

      if (selected.length > 0) {
        const selWords = selected.split(/\s+/).length;
        selectionStatusEl.textContent = `Selection: ${selWords} words (${selected.length} chars)`;
        selectionStatusEl.style.color = 'var(--primary)';

        // Auto-select "Selected Text Only" radio if present in active panel
        const activeScopeSelected = document.querySelector('.tool-form-panel.active input[value="selected"]');
        if (activeScopeSelected) {
          activeScopeSelected.checked = true;
        }
      } else {
        selectionStatusEl.textContent = 'Scope: Full document';
        selectionStatusEl.style.color = 'var(--text-muted)';
      }
    }

    if (textarea) {
      textarea.addEventListener('input', updateStats);
      textarea.addEventListener('select', updateSelectionStatus);
      textarea.addEventListener('mouseup', updateSelectionStatus);
      textarea.addEventListener('keyup', updateSelectionStatus);
      updateStats();
    }

    // ==========================================
    // 2. Editor Toolbar Utilities
    // ==========================================
    if (sampleBtn) {
      sampleBtn.addEventListener('click', () => {
        if (textarea) {
          textarea.value = SAMPLE_SCENE;
          updateStats();
          if (window.StoryVerse) {
            window.StoryVerse.showToast('Loaded sample manuscript scene.', 'info');
          }
        }
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        if (!textarea || !textarea.value.trim()) return;
        if (confirm('Are you sure you want to clear the editor?')) {
          textarea.value = '';
          updateStats();
          if (window.StoryVerse) {
            window.StoryVerse.showToast('Editor cleared.', 'info');
          }
        }
      });
    }

    if (copyEditorBtn) {
      copyEditorBtn.addEventListener('click', async () => {
        if (!textarea || !textarea.value) return;
        try {
          await navigator.clipboard.writeText(textarea.value);
          if (window.StoryVerse) {
            window.StoryVerse.showToast('Manuscript copied to clipboard.', 'success');
          }
        } catch {
          if (window.StoryVerse) {
            window.StoryVerse.showToast('Failed to copy to clipboard.', 'error');
          }
        }
      });
    }

    // Check URL parameters for project ID
    const urlParams = new URLSearchParams(window.location.search);
    const initialProjectId = urlParams.get('id');
    let isLoadingProject = false;

    if (initialProjectId) {
      loadProjectIntoEditor(initialProjectId);
    }

    async function loadProjectIntoEditor(id) {
      if (isLoadingProject) return;
      isLoadingProject = true;

      try {
        const res = await window.StoryVerseAPI.getProject(id);
        if (res.success && res.data) {
          activeProjectId = res.data.id;
          if (titleInput) titleInput.value = res.data.title || 'Untitled Project';
          if (textarea) textarea.value = res.data.generated_content || '';
          lastSavedContent = res.data.generated_content || '';
          updateStats();
          if (window.StoryVerse) {
            window.StoryVerse.showToast(`Loaded project #${id}: "${res.data.title}"`, 'info');
          }
        }
      } catch (err) {
        if (window.StoryVerse) {
          const isRateLimit = err.status === 429 || (err.message && err.message.toLowerCase().includes('too many requests'));
          const toastMsg = isRateLimit ? (err.message || 'Rate limit reached. Please wait a moment.') : `Could not load project #${id}.`;
          window.StoryVerse.showToast(toastMsg, isRateLimit ? 'warning' : 'error');
        }
      } finally {
        isLoadingProject = false;
      }
    }

    if (saveBtn) {
      saveBtn.addEventListener('click', async () => {
        const title = titleInput ? titleInput.value.trim() : 'Untitled Project';
        const content = textarea ? textarea.value : '';

        saveBtn.disabled = true;
        try {
          if (activeProjectId) {
            const updateRes = await window.StoryVerseAPI.updateProject(activeProjectId, {
              title: title,
              content: content,
              summary: 'Saved changes from Workspace'
            });
            if (!updateRes.success) {
              throw new Error(updateRes.message || 'Failed to update project.');
            }

            const contentChanged = content.trim() !== lastSavedContent.trim();
            lastSavedContent = content;
            if (!contentChanged && content.trim()) {
              await window.StoryVerseAPI.saveProjectVersion(activeProjectId, {
                content: content,
                summary: 'Manual version from Workspace'
              });
            }

            if (window.StoryVerse) {
              const versionMessage = content.trim() ? ' and saved new version.' : '.';
              window.StoryVerse.showToast(`Updated project "${title}"${versionMessage}`, 'success');
            }
          } else {
            const createRes = await window.StoryVerseAPI.createProject({
              title: title,
              content_type: 'story',
              content: content
            });

            if (createRes.success && createRes.data) {
              activeProjectId = createRes.data.id;
              lastSavedContent = content;
              window.history.replaceState(null, '', `?id=${activeProjectId}`);
              if (window.StoryVerse) {
                window.StoryVerse.showToast(`Project "${title}" created and saved to database!`, 'success');
              }
            }
          }
        } catch (err) {
          if (window.StoryVerse) {
            window.StoryVerse.showToast(err.message || 'Error saving project.', 'error');
          }
        } finally {
          saveBtn.disabled = false;
        }
      });
    }

    // Export dropdown toggle + per-format download
    const exportMenu = document.getElementById('exportDropdownMenu');
    if (exportBtn && exportMenu) {
      exportBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        exportMenu.style.display = exportMenu.style.display === 'none' ? 'flex' : 'none';
      });
      document.addEventListener('click', () => { exportMenu.style.display = 'none'; });

      exportMenu.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', async () => {
          const format = item.dataset.format;
          exportMenu.style.display = 'none';
          const title = titleInput ? titleInput.value.trim() : 'StoryVerse Document';
          const content = textarea ? textarea.value.trim() : '';
          if (!content) {
            if (window.StoryVerse) window.StoryVerse.showToast('No content to export.', 'warning');
            return;
          }
          item.disabled = true;
          try {
            if (window.StoryVerse) window.StoryVerse.showToast(`Preparing ${format.toUpperCase()} download...`, 'info');
            await window.StoryVerseAPI.exportDocument(format, {
              title: title || 'StoryVerse Document',
              content: content,
              project_id: activeProjectId || undefined
            });
            if (window.StoryVerse) window.StoryVerse.showToast(`${format.toUpperCase()} downloaded successfully.`, 'success');
          } catch (err) {
            if (window.StoryVerse) window.StoryVerse.showToast(err.message || 'Export failed.', 'error');
          } finally {
            item.disabled = false;
          }
        });
      });
    }

    // ==========================================
    // 3. Tool Switching Navigation
    // ==========================================
    toolPills.forEach(pill => {
      pill.addEventListener('click', () => {
        const tool = pill.dataset.tool;
        if (!tool) return;

        toolPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');

        toolFormPanels.forEach(panel => {
          panel.classList.remove('active');
          panel.style.display = 'none';
        });

        const targetPanel = document.getElementById(`form-${tool}`);
        if (targetPanel) {
          targetPanel.classList.add('active');
          targetPanel.style.display = 'flex';
        }
      });
    });

    // ==========================================
    // 4. Loading States & Helpers
    // ==========================================
    function setLoading(isLoading, text = 'Generating with AI...', activeBtn = null) {
      if (assistantLoading) {
        assistantLoading.style.display = isLoading ? 'flex' : 'none';
        if (assistantLoadingText) {
          assistantLoadingText.textContent = text;
        }
      }
      if (activeBtn) {
        activeBtn.disabled = isLoading;
      }
    }

    function getTargetContent(scopeRadioName) {
      if (!textarea) return { text: '', isSelection: false, start: 0, end: 0 };

      const selStart = textarea.selectionStart;
      const selEnd = textarea.selectionEnd;
      const selected = textarea.value.substring(selStart, selEnd).trim();
      const scopeRadio = document.querySelector(`input[name="${scopeRadioName}"]:checked`);
      const wantsSelected = scopeRadio && scopeRadio.value === 'selected';

      if (wantsSelected && selected.length > 0) {
        return {
          text: selected,
          isSelection: true,
          start: selStart,
          end: selEnd
        };
      }

      return {
        text: textarea.value.trim(),
        isSelection: false,
        start: 0,
        end: textarea.value.length
      };
    }

    // ==========================================
    // 5. Result Presentation & Comparison
    // ==========================================
    function displayAssistantResult({
      operation,
      original,
      generated,
      icon = '✨',
      title = 'AI Assistant Output',
      model = 'Gemini Pro',
      tokens = null,
      isSelection = false,
      selStart = 0,
      selEnd = 0
    }) {
      if (!aiResultCard) return;

      currentResult = {
        operation,
        originalText: original || '',
        generatedText: generated || '',
        isSelection,
        selectionStart: selStart,
        selectionEnd: selEnd
      };

      if (resultIcon) resultIcon.textContent = icon;
      if (resultHeading) resultHeading.textContent = title;
      if (badgeOperation) badgeOperation.textContent = operation.toUpperCase();
      if (badgeModel) {
        badgeModel.textContent = tokens ? `${model} • ${tokens} tokens` : model;
      }

      // Safe rendering using textContent (prevent XSS)
      if (resultOutputText) {
        resultOutputText.textContent = generated;
      }
      if (comparisonOriginalText) {
        comparisonOriginalText.textContent = original || '(No prior text)';
      }
      if (comparisonGeneratedText) {
        comparisonGeneratedText.textContent = generated;
      }

      // Reset view to single output
      switchResultView('generated');

      aiResultCard.style.display = 'block';
      aiResultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function switchResultView(viewName) {
      viewTabBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === viewName);
      });

      if (viewName === 'comparison') {
        if (viewSingleOutput) viewSingleOutput.style.display = 'none';
        if (viewComparison) viewComparison.style.display = 'grid';
      } else {
        if (viewSingleOutput) viewSingleOutput.style.display = 'block';
        if (viewComparison) viewComparison.style.display = 'none';
      }
    }

    viewTabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const view = btn.dataset.view;
        if (view) switchResultView(view);
      });
    });

    if (btnDismissResult) {
      btnDismissResult.addEventListener('click', () => {
        if (aiResultCard) aiResultCard.style.display = 'none';
      });
    }

    if (btnCopyResult) {
      btnCopyResult.addEventListener('click', async () => {
        if (!currentResult.generatedText) return;
        try {
          await navigator.clipboard.writeText(currentResult.generatedText);
          if (window.StoryVerse) {
            window.StoryVerse.showToast('AI output copied to clipboard.', 'success');
          }
        } catch {
          if (window.StoryVerse) {
            window.StoryVerse.showToast('Failed to copy to clipboard.', 'error');
          }
        }
      });
    }

    if (btnReplaceText) {
      btnReplaceText.addEventListener('click', () => {
        if (!textarea || !currentResult.generatedText) return;

        if (currentResult.isSelection) {
          const val = textarea.value;
          textarea.value =
            val.substring(0, currentResult.selectionStart) +
            currentResult.generatedText +
            val.substring(currentResult.selectionEnd);
        } else {
          textarea.value = currentResult.generatedText;
        }

        updateStats();
        if (window.StoryVerse) {
          window.StoryVerse.showToast('Editor manuscript updated with AI output.', 'success');
        }
      });
    }

    if (btnAppendText) {
      btnAppendText.addEventListener('click', () => {
        if (!textarea || !currentResult.generatedText) return;

        const currentVal = textarea.value.trim();
        textarea.value = currentVal ? `${currentVal}\n\n${currentResult.generatedText}` : currentResult.generatedText;
        updateStats();
        if (window.StoryVerse) {
          window.StoryVerse.showToast('AI output appended to end of manuscript.', 'success');
        }
      });
    }

    // ==========================================
    // 6. Tool Handlers Execution
    // ==========================================

    // Tool 1: Rewrite
    if (btnExecuteRewrite) {
      btnExecuteRewrite.addEventListener('click', async () => {
        const { text, isSelection, start, end } = getTargetContent('rewriteScope');
        if (!text) {
          if (window.StoryVerse) window.StoryVerse.showToast('Please type or select text to rewrite.', 'warning');
          return;
        }

        const styleSelect = document.getElementById('rewriteStyle');
        const langSelect = document.getElementById('rewriteLanguage');
        const style = styleSelect ? styleSelect.value : 'improve clarity';
        const language = langSelect && langSelect.value ? langSelect.value : undefined;

        setLoading(true, 'Rewriting text with Gemini AI...', btnExecuteRewrite);
        try {
          const response = await window.StoryVerseAPI.rewriteText({
            content: text,
            style: style,
            language: language
          });

          if (response.success && response.data) {
            displayAssistantResult({
              operation: 'Rewrite',
              original: text,
              generated: response.data.rewritten,
              icon: '🔄',
              title: `Rewritten (${response.data.style || style})`,
              model: response.data.metadata?.model || 'Gemini',
              tokens: response.data.metadata?.tokens_used,
              isSelection,
              selStart: start,
              selEnd: end
            });
            if (window.StoryVerse) window.StoryVerse.showToast('Rewrite completed successfully.', 'success');
          } else {
            throw new Error(response.message || 'Rewrite failed.');
          }
        } catch (err) {
          if (window.StoryVerse) window.StoryVerse.showToast(err.message || 'Error executing rewrite.', 'error');
        } finally {
          setLoading(false, '', btnExecuteRewrite);
        }
      });
    }

    // Tool 2: Translate
    if (btnExecuteTranslate) {
      btnExecuteTranslate.addEventListener('click', async () => {
        const { text, isSelection, start, end } = getTargetContent('translateScope');
        if (!text) {
          if (window.StoryVerse) window.StoryVerse.showToast('Please type or select text to translate.', 'warning');
          return;
        }

        const langSelect = document.getElementById('translateTargetLang');
        const targetLang = langSelect ? langSelect.value : 'Telugu';

        setLoading(true, `Translating into ${targetLang}...`, btnExecuteTranslate);
        try {
          const response = await window.StoryVerseAPI.translateText({
            content: text,
            target_language: targetLang
          });

          if (response.success && response.data) {
            displayAssistantResult({
              operation: 'Translate',
              original: text,
              generated: response.data.translation,
              icon: '🌐',
              title: `Translation → ${targetLang}`,
              model: response.data.metadata?.model || 'Gemini',
              tokens: response.data.metadata?.tokens_used,
              isSelection,
              selStart: start,
              selEnd: end
            });
            if (window.StoryVerse) window.StoryVerse.showToast(`Translated to ${targetLang}.`, 'success');
          } else {
            throw new Error(response.message || 'Translation failed.');
          }
        } catch (err) {
          if (window.StoryVerse) window.StoryVerse.showToast(err.message || 'Error executing translation.', 'error');
        } finally {
          setLoading(false, '', btnExecuteTranslate);
        }
      });
    }

    // Tool 3: Summarize
    if (btnExecuteSummarize) {
      btnExecuteSummarize.addEventListener('click', async () => {
        const text = textarea ? textarea.value.trim() : '';
        if (!text) {
          if (window.StoryVerse) window.StoryVerse.showToast('Please type manuscript text to summarize.', 'warning');
          return;
        }

        const lenSelect = document.getElementById('summarizeLength');
        const langSelect = document.getElementById('summarizeLanguage');
        const length = lenSelect ? lenSelect.value : 'medium';
        const language = langSelect && langSelect.value ? langSelect.value : undefined;

        setLoading(true, 'Synthesizing literary summary...', btnExecuteSummarize);
        try {
          const response = await window.StoryVerseAPI.summarizeText({
            content: text,
            summary_length: length,
            language: language
          });

          if (response.success && response.data) {
            displayAssistantResult({
              operation: 'Summarize',
              original: text,
              generated: response.data.summary,
              icon: '📝',
              title: `Summary (${length.toUpperCase()})`,
              model: response.data.metadata?.model || 'Gemini',
              tokens: response.data.metadata?.tokens_used,
              isSelection: false
            });
            if (window.StoryVerse) window.StoryVerse.showToast('Summary generated successfully.', 'success');
          } else {
            throw new Error(response.message || 'Summarization failed.');
          }
        } catch (err) {
          if (window.StoryVerse) window.StoryVerse.showToast(err.message || 'Error generating summary.', 'error');
        } finally {
          setLoading(false, '', btnExecuteSummarize);
        }
      });
    }

    // Tool 4: Generate Dialogue
    if (btnExecuteDialogue) {
      btnExecuteDialogue.addEventListener('click', async () => {
        const text = textarea ? textarea.value.trim() : '';
        const charInput = document.getElementById('dialogueCharacters');
        const genreSelect = document.getElementById('dialogueGenre');
        const toneSelect = document.getElementById('dialogueTone');
        const langSelect = document.getElementById('dialogueLanguage');

        const characters = charInput ? charInput.value.trim() : 'Two characters';
        const genre = genreSelect ? genreSelect.value : 'Drama';
        const tone = toneSelect ? toneSelect.value : 'Tense';
        const language = langSelect ? langSelect.value : 'English';

        // Context uses editor text if available
        const context = text || 'A dramatic turning point between characters';

        setLoading(true, 'Crafting dynamic dialogue...', btnExecuteDialogue);
        try {
          const response = await window.StoryVerseAPI.generateDialogue({
            context: context,
            characters: characters,
            genre: genre,
            tone: tone,
            language: language
          });

          if (response.success && response.data) {
            displayAssistantResult({
              operation: 'Dialogue',
              original: context,
              generated: response.data.dialogue,
              icon: '💬',
              title: `Dialogue: ${characters}`,
              model: response.data.metadata?.model || 'Gemini',
              tokens: response.data.metadata?.tokens_used,
              isSelection: false
            });
            if (window.StoryVerse) window.StoryVerse.showToast('Dialogue generated successfully.', 'success');
          } else {
            throw new Error(response.message || 'Dialogue generation failed.');
          }
        } catch (err) {
          if (window.StoryVerse) window.StoryVerse.showToast(err.message || 'Error generating dialogue.', 'error');
        } finally {
          setLoading(false, '', btnExecuteDialogue);
        }
      });
    }

    // Tool 5: Plot Twist
    if (btnExecuteTwist) {
      btnExecuteTwist.addEventListener('click', async () => {
        const text = textarea ? textarea.value.trim() : '';
        const genreSelect = document.getElementById('twistGenre');
        const toneSelect = document.getElementById('twistTone');
        const langSelect = document.getElementById('twistLanguage');

        const genre = genreSelect ? genreSelect.value : 'Science Fiction';
        const tone = toneSelect ? toneSelect.value : 'Suspenseful';
        const language = langSelect ? langSelect.value : 'English';
        const premise = text || 'An astronomer receives an alien signal from deep space.';

        setLoading(true, 'Conceiving narrative plot twists...', btnExecuteTwist);
        try {
          const response = await window.StoryVerseAPI.generatePlotTwist({
            premise: premise,
            genre: genre,
            tone: tone,
            language: language
          });

          if (response.success && response.data) {
            displayAssistantResult({
              operation: 'Plot Twist',
              original: premise,
              generated: response.data.plot_twists,
              icon: '⚡',
              title: `Plot Twists (${genre} • ${tone})`,
              model: response.data.metadata?.model || 'Gemini',
              tokens: response.data.metadata?.tokens_used,
              isSelection: false
            });
            if (window.StoryVerse) window.StoryVerse.showToast('Plot twists generated.', 'success');
          } else {
            throw new Error(response.message || 'Plot twist generation failed.');
          }
        } catch (err) {
          if (window.StoryVerse) window.StoryVerse.showToast(err.message || 'Error generating plot twist.', 'error');
        } finally {
          setLoading(false, '', btnExecuteTwist);
        }
      });
    }

    // Tool 6: Continue Writing
    if (btnExecuteContinue) {
      btnExecuteContinue.addEventListener('click', async () => {
        const text = textarea ? textarea.value.trim() : '';
        if (!text) {
          if (window.StoryVerse) window.StoryVerse.showToast('Please type some manuscript text first so the AI can continue it.', 'warning');
          return;
        }

        const dirInput = document.getElementById('continueDirection');
        const toneSelect = document.getElementById('continueTone');
        const langSelect = document.getElementById('continueLanguage');

        const direction = dirInput && dirInput.value.trim() ? dirInput.value.trim() : undefined;
        const tone = toneSelect && toneSelect.value ? toneSelect.value : undefined;
        const language = langSelect && langSelect.value ? langSelect.value : undefined;

        setLoading(true, 'Continuing your narrative...', btnExecuteContinue);
        try {
          const response = await window.StoryVerseAPI.continueWriting({
            content: text,
            direction: direction,
            tone: tone,
            language: language
          });

          if (response.success && response.data) {
            displayAssistantResult({
              operation: 'Continue',
              original: text,
              generated: response.data.continuation,
              icon: '✍️',
              title: 'Narrative Continuation',
              model: response.data.metadata?.model || 'Gemini',
              tokens: response.data.metadata?.tokens_used,
              isSelection: false
            });
            if (window.StoryVerse) window.StoryVerse.showToast('Continuation written.', 'success');
          } else {
            throw new Error(response.message || 'Continuation failed.');
          }
        } catch (err) {
          if (window.StoryVerse) window.StoryVerse.showToast(err.message || 'Error continuing story.', 'error');
        } finally {
          setLoading(false, '', btnExecuteContinue);
        }
      });
    }

  });
})();
