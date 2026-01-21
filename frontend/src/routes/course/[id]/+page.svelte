<script lang="ts">
    import { invalidateAll } from '$app/navigation';
    
    export let data; 

    // --- UPLOAD STATE ---
    let fileInput: HTMLInputElement;
    let activeTab = "upload"; 
    let pastedText = "";
    let uploadStatus = "";
    
    // --- FILTER STATE ---
    let selectedCategory = "All";

    // --- REACTIVE HELPERS ---
    
    // 1. Calculate Progress Bar
    $: totalModules = data.course.modules.length;
    $: completedModules = data.course.modules.filter(m => m.completed).length;
    $: progressPercentage = totalModules === 0 ? 0 : Math.round((completedModules / totalModules) * 100);

    // 2. Extract unique categories
    $: categories = ["All", ...new Set(data.course.modules
        .map(m => {
            const match = m.title.match(/^\[(.*?)\]/);
            return match ? match[1] : null;
        })
        .filter(c => c !== null)
    )];

    // 3. Create filtered list
    $: filteredModules = selectedCategory === "All"
        ? data.course.modules
        : data.course.modules.filter(m => m.title.startsWith(`[${selectedCategory}]`));

    // --- ACTIONS ---

    // NEW: Toggle Checkbox
    async function toggleCompletion(module) {
        // Optimistic UI Update (Change it instantly before server responds)
        module.completed = !module.completed;
        data.course.modules = data.course.modules; // Trigger Svelte reactivity

        try {
            const res = await fetch(`http://127.0.0.1:5000/api/modules/${module.id}/toggle`, {
                method: 'POST'
            });
            if (!res.ok) {
                // Revert if server failed
                module.completed = !module.completed;
                alert("Failed to save progress");
            } else {
                // If we don't invalidate, the progress bar works via local reactivity
                // If you want to be super safe, you can uncomment this:
                // await invalidateAll(); 
            }
        } catch (e) {
            module.completed = !module.completed;
        }
    }

    async function handleUpload() {
        const formData = new FormData();
        formData.append('course_id', data.course.id); 

        if (activeTab === 'upload') {
            if (!fileInput.files || fileInput.files.length === 0) return alert("Select a file");
            formData.append('file', fileInput.files[0]);
        } else {
            if (!pastedText.trim()) return alert("Paste text");
            formData.append('raw_text', pastedText);
        }

        uploadStatus = "Processing...";

        try {
            const res = await fetch('http://127.0.0.1:5000/api/upload-mit-assignments', {
                method: 'POST',
                body: formData
            });
            const result = await res.json();

            if (res.ok) {
                uploadStatus = "Success! " + result.message;
                if (fileInput) fileInput.value = ""; 
                pastedText = "";
                await invalidateAll(); 
                selectedCategory = "All";
            } else {
                uploadStatus = "Error: " + result.error;
            }
        } catch (err) {
            uploadStatus = "Error: Could not connect to backend.";
        }
    }
</script>

<div class="max-w-4xl mx-auto p-8">
    <a href="/" class="text-gray-500 hover:text-blue-600 hover:underline mb-4 inline-block transition-colors">&larr; Back to Dashboard</a>

    <div class="mb-8">
        <div class="flex justify-between items-end mb-2">
            <h1 class="text-4xl font-bold text-blue-900">{data.course.title}</h1>
            <span class="text-lg font-semibold text-blue-600">{progressPercentage}% Complete</span>
        </div>
        
        <div class="w-full bg-gray-200 rounded-full h-4 overflow-hidden shadow-inner">
            <div 
                class="bg-green-500 h-4 rounded-full transition-all duration-500 ease-out" 
                style="width: {progressPercentage}%"
            ></div>
        </div>
    </div>

    <div class="border rounded-xl bg-gray-50 mb-10 shadow-sm overflow-hidden">
        <div class="flex border-b border-gray-200">
            <button on:click={() => activeTab = 'upload'} class="flex-1 py-3 text-sm font-medium transition-colors {activeTab === 'upload' ? 'bg-white text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 bg-gray-50 hover:bg-gray-100'}">MIT File Upload</button>
            <button on:click={() => activeTab = 'paste'} class="flex-1 py-3 text-sm font-medium transition-colors {activeTab === 'paste' ? 'bg-white text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 bg-gray-50 hover:bg-gray-100'}">Coursera / edX Paste</button>
        </div>
        <div class="p-6">
            {#if activeTab === 'upload'}
                <div class="flex flex-col sm:flex-row gap-3">
                    <input type="file" bind:this={fileInput} class="border bg-white p-2 rounded flex-grow text-sm"/>
                    <button on:click={handleUpload} class="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">Upload</button>
                </div>
            {:else}
                <div class="flex flex-col gap-3">
                    <textarea bind:value={pastedText} rows="4" placeholder="Paste syllabus text here..." class="w-full border p-3 rounded text-sm"></textarea>
                    <button on:click={handleUpload} class="bg-blue-600 text-white px-6 py-2 rounded self-end hover:bg-blue-700">Import</button>
                </div>
            {/if}
            {#if uploadStatus} <p class="mt-3 text-sm {uploadStatus.includes('Error') ? 'text-red-600' : 'text-green-600'}">{uploadStatus}</p> {/if}
        </div>
    </div>

    <div class="flex flex-wrap gap-2 mb-6">
        {#each categories as category}
            <button 
                on:click={() => selectedCategory = category}
                class="px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200 border {selectedCategory === category ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-100'}"
            >
                {category}
            </button>
        {/each}
    </div>

    <div class="grid gap-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
        {#each filteredModules as module}
            <div class="bg-white border border-gray-200 rounded-lg p-5 shadow-sm hover:shadow-md transition-all duration-200 group flex gap-4 {module.completed ? 'opacity-60 bg-gray-50' : ''}">
                
                <div class="pt-1">
                    <input 
                        type="checkbox" 
                        checked={module.completed} 
                        on:change={() => toggleCompletion(module)}
                        class="w-6 h-6 text-blue-600 rounded focus:ring-blue-500 cursor-pointer"
                    />
                </div>

                <div class="flex-1">
                    <h3 class="font-bold text-lg text-gray-900 group-hover:text-blue-800 transition-colors {module.completed ? 'line-through text-gray-500' : ''}">
                        {@html module.title.replace(/^\[(.*?)\]/, '<span class="text-gray-400 text-sm font-medium uppercase tracking-wide mr-2 no-underline">$1</span>')}
                    </h3>
                    
                    {#if module.content.trim().startsWith('http')}
                        <div class="mt-3">
                            <a href={module.content} target="_blank" class="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-4 py-2 rounded-md hover:bg-blue-100 text-sm font-medium border border-blue-200">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                                Open Resource
                            </a>
                        </div>
                    {:else}
                        <p class="whitespace-pre-wrap text-gray-600 mt-2 leading-relaxed">{module.content}</p>
                    {/if}
                </div>
            </div>
        {/each}
    </div>
</div>