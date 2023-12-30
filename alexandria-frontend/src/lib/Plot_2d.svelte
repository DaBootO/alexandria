<script>
    import * as d3 from 'd3';
    export let data;
    export let width = 640;
    export let height = 400;
    export let marginTop = 20;
    export let marginRight = 20;
    export let marginBottom = 30;
    export let marginLeft = 40;

    let gx;
    let gy;

    // Transforming the data to be compatible with d3.line
    $: formattedData = data.map(d => d.x.map((x, i) => ({x, y: d.y[i]})));

    $: x = d3.scaleLinear()
        .domain(d3.extent(formattedData.flat(), d => d.x))
        .range([marginLeft, width - marginRight]);

    $: y = d3.scaleLinear()
        .domain(d3.extent(formattedData.flat(), d => d.y))
        .range([height - marginBottom, marginTop]);

    $: line = d3.line()
        .x(d => x(d.x))
        .y(d => y(d.y));

    $: d3.select(gy).call(d3.axisLeft(y));
    $: d3.select(gx).call(d3.axisBottom(x));
</script>

<svg {width} {height}>
    <g bind:this={gx} transform="translate(0,{height - marginBottom})" />
    <g bind:this={gy} transform="translate({marginLeft},0)" />
    {#each formattedData as d, i}
        <path fill="none" stroke="currentColor" stroke-width="3.5" d={line(d)} />
        <g fill="white" stroke="#00FF00" stroke-width="1.5">
            {#each d as point, j}
                <circle key={i + '-' + j} cx={x(point.x)} cy={y(point.y)} r="2.5" />
            {/each}
        </g>
    {/each}
</svg>
