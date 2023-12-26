<script>
    import DataTable from "$lib/DataTable.svelte";
    const test = [
        {"col_name": "col1", "data": [1,2,3,4]},
        {"col_name": "col2", "data": [5,6,7,8]},
        {"col_name": "col3", "data": [1,2,3,4]},
    ];
</script>

<div class="flex-col">
    <div class="text-xl">Data Viewer</div>
    <DataTable data={test} />
</div>
