<script>
    // data is json array
    export let data;
</script>

<div class="overflow-x-auto">
    <table class="table table-xs table-pin-rows table-pin-cols">
        <thead>
            {#each data as col}
                <th class="w-auto">{col.col_name}</th>
            {/each}
        </thead>
        <thead>
            {#each data as col}
                <th class="w-auto">{col.type}</th>
            {/each}
        </thead>
        <thead>
            {#each data as col}
                <th></th>
            {/each}
        </thead>
        <tbody>
            {#each data[0].data as col, i}
                <tr>
                    {#each data as dat, j}
                        <th>{dat.data[i]}</th>
                    {/each}
                </tr>
            {/each}
        </tbody>
        <!-- <tfoot>
            <tr>
                <th></th>
                <td>Name</td>
                <td>Job</td>
                <td>company</td>
                <td>location</td>
                <td>Last Login</td>
                <td>Favorite Color</td>
                <th></th>
            </tr>
        </tfoot> -->
    </table>
</div>
