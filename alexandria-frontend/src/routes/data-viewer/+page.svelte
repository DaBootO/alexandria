<script>
    import DataTable from "$lib/DataTable.svelte";
    const test = [
        {"col_name": "col1", "type": "numeric", "data": [1,2,3,4]},
        {"col_name": "col1", "type": "numeric", "data": [1,2,3,4]},
        {"col_name": "col1", "type": "numeric", "data": [1,2,3,4]},
    ];
</script>

<div class="flex-col m-2">
    <div class="text-xl">Data Viewer</div>
    <DataTable data={test} />
</div>
