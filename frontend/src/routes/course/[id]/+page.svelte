<script lang="ts">
    import { invalidateAll } from '$app/navigation';
    
    // This 'data' variable comes from the file above (+page.ts)
    // It contains the specific row from your database.
    export let data; 
    
    let fileInput: HTMLInputElement;
    let uploadStatus = "";

async function handleUpload() {
        if (!fileInput.files || fileInput.files.length === 0) return;

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('course_id', data.course.id);

        uploadStatus = "Uploading...";

        const res = await fetch('http://127.0.0.1:5000/api/upload-mit-assignments', {
            method: 'POST',
            body: formData
        });

        const result = await res.json();
        
        if (res.ok) {
            // SHOW THE EXACT MESSAGE FROM BACKEND
            alert(result.message); // e.g. "Successfully imported 0 assignments"
            
            uploadStatus = result.message;
            fileInput.value = ""; 
            await invalidateAll();
        } else {
            uploadStatus = "Error: " + result.error;
        }
    }
</script>

<div class="max-w-4xl mx-auto p-8">
    <a href="/" class="text-gray-500 hover:underline mb-4 block">&larr; Back to Dashboard</a>

    <h1 class="text-4xl font-bold mb-6 text-blue-900">{data.course.title}</h1>

    <div class="border p-6 rounded-lg bg-gray-50 mb-8">
        <h3 class="font-bold mb-2">Import MIT Syllabus HTML</h3>
        <div class="flex gap-2">
            <input type="file" bind:this={fileInput} class="border bg-white p-1 rounded" />
            <button on:click={handleUpload} class="bg-blue-600 text-white px-4 py-1 rounded hover:bg-blue-700">
                Upload
            </button>
        </div>
        {#if uploadStatus} <p class="mt-2 text-sm text-gray-600">{uploadStatus}</p> {/if}
    </div>

    <h2 class="text-2xl font-bold mb-4">Assignments</h2>
    
    {#if data.course.modules.length === 0}
        <div class="text-gray-500 italic p-4 border border-dashed rounded">
            No assignments yet. Upload the syllabus above!
        </div>
    {:else}
        <div class="space-y-4">
            <h2 class="text-2xl font-bold mb-4">Assignments & Resources</h2>
    
    {#if data.course.modules.length === 0}
        <div class="text-gray-500 italic p-6 border-2 border-dashed border-gray-200 rounded-lg text-center">
            No assignments found. Try uploading a syllabus HTML file above!
        </div>
    {:else}
        <div class="grid gap-4">
            {#each data.course.modules as module}
                <div class="bg-white border border-gray-200 rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow duration-200">
                    <div class="flex justify-between items-start">
                        <div class="flex-1">
                            <h3 class="font-bold text-lg text-gray-900">{module.title}</h3>
                            
                            {#if module.content.trim().startsWith('http')}
                                <div class="mt-3">
                                    <a 
                                        href={module.content} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        class="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-4 py-2 rounded-md hover:bg-blue-100 transition-colors font-medium text-sm border border-blue-200"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                        </svg>
                                        Open Resource
                                    </a>
                                    <div class="text-xs text-gray-400 mt-2 font-mono truncate max-w-xl">
                                        {module.content}
                                    </div>
                                </div>
                            {:else}
                                <p class="whitespace-pre-wrap text-gray-600 mt-2 leading-relaxed">{module.content}</p>
                            {/if}
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
        </div>
    {/if}
</div>