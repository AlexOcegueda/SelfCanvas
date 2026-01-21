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

        if (res.ok) {
            uploadStatus = "Success!";
            fileInput.value = ""; 
            await invalidateAll(); 
        } else {
            const result = await res.json();
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
            {#each data.course.modules as module}
                <div class="bg-white border rounded p-4 shadow-sm">
                    <h3 class="font-bold text-lg">{module.title}</h3>
                    <p class="whitespace-pre-wrap text-gray-700 mt-2">{module.content}</p>
                </div>
            {/each}
        </div>
    {/if}
</div>