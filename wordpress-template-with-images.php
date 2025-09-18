<?php
/**
 * Template Name: Custom Front Page
 */

get_header();
?>

<!-- Load Font Awesome -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">

<?php
if ( have_posts() ) :
    while ( have_posts() ) : the_post();

        $content = get_the_content();

        // Extract JSON data
        $json_data = '';
        if ( preg_match('/<pre id="structured-json">(.*?)<\/pre>/s', $content, $matches) ) {
            $json_data = trim($matches[1]);
        }

        $decoded = $json_data ? json_decode($json_data, true) : [];

        // Load categories.json to maintain category order
        $categories_json = file_get_contents(get_template_directory() . '/config/categories.json');
        $categories_data = json_decode($categories_json, true);
        $category_order = $categories_data['categories'] ?? [];

        ?>

        <div class="entry-content">
            <?php
// Get yesterday's date in 'F j, Y' format
$yesterday_date = date('F j, Y', strtotime('-1 day'));

// Query for the post from yesterday
$args = array(
    'date_query' => array(
        array(
            'after'     => date('Y-m-d', strtotime('-2 days')) . ' 23:59:59',
            'before'    => date('Y-m-d', strtotime('-1 day')) . ' 23:59:59',
            'inclusive' => true,
        ),
    ),
    'posts_per_page' => 1,
);
$yesterday_query = new WP_Query($args);

// Check if a post exists for yesterday
if ($yesterday_query->have_posts()) {
    $yesterday_query->the_post();
    $yesterday_link = get_permalink();
    $yesterday_text = "View " . $yesterday_date;
} else {
    $yesterday_link = "#";
    $yesterday_text = "No earlier posts";
}

// Reset Post Data
wp_reset_postdata();
?>

<h1 class="page-title">
    <?php echo date('F j, Y'); ?>
    <a href="<?php echo esc_url($yesterday_link); ?>" 
       style="font-size: 14px; margin-left: 10px; text-decoration: none; color: #0073aa;">
        <?php echo esc_html($yesterday_text); ?>
    </a>
</h1>


            <?php if (!empty($decoded) && is_array($decoded)) :

                // Separate "Headline News" from general categories
                $headline_articles = [];
                $general_categories = [];

                foreach ($decoded as $category_block) {
                    if ($category_block['category'] === 'Headline News') {
                        foreach ($category_block['articles'] as $article) {
                            if (in_array($article['headline'], ["Headline 1", "Headline 2", "Headline 3", "Headline 4"])) {
                                $headline_articles[] = $article;
                            }
                        }
                    } else {
                        $general_categories[$category_block['category']] = $category_block['articles'];
                    }
                }

                // Display Headline News with dynamic layout based on article count
                if (!empty($headline_articles)):
                    usort($headline_articles, function($a, $b) {
                        $headline_order = ["Headline 1" => 1, "Headline 2" => 2, "Headline 3" => 3, "Headline 4" => 4];
                        return ($headline_order[$a['headline']] ?? 99) <=> ($headline_order[$b['headline']] ?? 99);
                    });

                    $headline_count = count($headline_articles);
                    ?>
                    <section class="headline-news">
                        <h2 class="category-title">Headline News</h2>
                        <div class="headline-grid" style="display: grid; grid-template-columns: <?php echo ($headline_count === 1) ? '1fr' : (($headline_count === 2) ? '1fr 1fr' : '1fr 1fr 1fr'); ?>; gap: 20px;">
                            <?php foreach ($headline_articles as $article): ?>
                                <div class="headline-article">
                                    <a href="<?php echo esc_url($article['link']); ?>" target="_blank">
                                        <?php if (!empty($article['image'])): ?>
                                            <img src="<?php echo esc_url($article['image']); ?>" alt="<?php echo esc_attr($article['title']); ?>" style="width: 100%; display: block;">
                                        <?php endif; ?>
                                        <h2><?php echo esc_html($article['title']); ?></h2>
                                    </a>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    </section>
                <?php endif;

                // ✅ Organize articles by category and distribute into three columns
                $columns = [[], [], []];
                $column_index = 0;

                foreach ($general_categories as $category => $articles) {
                    $columns[$column_index][] = ['category' => $category, 'articles' => $articles];
                    $column_index = ($column_index + 1) % 3;
                }
                ?>

                <div class="general-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
                    <?php foreach ($columns as $column): ?>
                        <div class="column">
                            <?php foreach ($column as $category_block): ?>
                                <h2 class="category-title" style="border-bottom: 2px solid #000; padding-bottom: 5px;">
                                    <?php echo esc_html($category_block['category']); ?>
                                </h2>
                                <?php 
                                $article_count = 0;
                                foreach ($category_block['articles'] as $article): 
                                    $article_count++;
                                    $headline_type = $article['headline'] ?? '';
                                    $image_url = !empty($article['image']) ? esc_url($article['image']) : '';

                                    // ✅ IMAGE STRATEGY: Show images for headline articles, every 3rd article, and every 5th gets full width
                                    $is_headline = in_array($headline_type, ["Headline 1", "Headline 2", "Headline 3", "Headline 4"]);
                                    $show_small_image = ($article_count % 3 == 0) || $is_headline;
                                    $show_full_width_image = ($article_count % 5 == 0);
                                    $show_medium_image = ($article_count % 7 == 0);

                                    // Determine layout based on headline type and image strategy
                                    $is_full_width = ($headline_type === 'Headline 1') || $show_full_width_image;
                                    $has_side_image = in_array($headline_type, ["Headline 2", "Headline 3", "Headline 4"]) || $show_small_image || $show_medium_image;

                                    // Determine image size based on position and type
                                    $image_size = '75px'; // default small
                                    if ($show_full_width_image || $headline_type === 'Headline 1') {
                                        $image_size = '100%';
                                    } else if ($show_medium_image || in_array($headline_type, ["Headline 2", "Headline 3"])) {
                                        $image_size = '90px';
                                    } else if ($article_count % 11 == 0) {
                                        $image_size = '110px'; // occasional larger images for rhythm
                                    }
                                ?>
                                    <div class="article-item" style="display: flex; flex-direction: <?php echo $is_full_width ? 'column' : 'row'; ?>; align-items: center; gap: 10px; margin-bottom: 10px;">
                                        
                                        <?php if ($image_url && ($is_full_width || $has_side_image)): ?>
                                            <img src="<?php echo $image_url; ?>" alt="<?php echo esc_attr($article['title']); ?>" 
                                                 style="width: <?php echo $image_size; ?>; 
                                                        display: block; 
                                                        margin-right: <?php echo $is_full_width ? '0' : '10px'; ?>;
                                                        border-radius: <?php echo ($image_size == '100%') ? '8px' : '4px'; ?>;
                                                        box-shadow: <?php echo ($image_size == '100%') ? '0 4px 8px rgba(0,0,0,0.2)' : '0 2px 4px rgba(0,0,0,0.1)'; ?>;">
                                        <?php endif; ?>

                                       <a href="<?php echo esc_url($article['link']); ?>" target="_blank" 
                                         class="article-link" 
                                         style="text-decoration: none; font-weight: <?php echo in_array($article['headline'], ["Headline 1", "Headline 2", "Headline 3", "Headline 4"]) ? 'bold' : 'normal'; ?>;">
                                          <span><?php echo esc_html($article['title']); ?></span>
                                          <i class="fas fa-comment-dots news-icon" 
                                             style="color: #7d7d7d;" 
                                             data-summary="<?php echo esc_attr($article['summary']); ?>" 
                                             data-image="<?php echo !empty($article['image']) ? esc_url($article['image']) : ''; ?>">
                                          </i>
                                      </a>
                                      <span class="news-source" style="display: none;"><?php echo esc_html($article['source']); ?></span>

                                    </div>
                                <?php endforeach; ?>
                            <?php endforeach; ?>
                        </div>
                    <?php endforeach; ?>
                </div>

            <?php else :
                // Fallback: Show latest post if no JSON is found
                $latest_args = array(
                    'posts_per_page' => 1,
                );
                $latest_query = new WP_Query($latest_args);
                if ($latest_query->have_posts()) :
                    while ($latest_query->have_posts()) : $latest_query->the_post();
                        echo '<h2><a href="' . esc_url(get_permalink()) . '">' . esc_html(get_the_title()) . '</a></h2>';
                        echo '<div>' . get_the_excerpt() . '</div>';
                    endwhile;
                    wp_reset_postdata();
                else :
                    echo '<p>No posts found.</p>';
                endif;
            endif; ?>
        </div><!-- .entry-content -->

        <!-- Tooltip Fix -->
<script>
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll('.news-icon').forEach(icon => {
            icon.addEventListener('mouseenter', function (e) {
                let summary = e.target.getAttribute('data-summary') || "No summary available.";
                let imageUrl = e.target.getAttribute('data-image') || '';
                let newsLink = e.target.closest('.article-item')?.querySelector('.article-link')?.href || '#';

                // Extract the root domain from the news link
                let newsSource = "Unknown Source";
                try {
                    let url = new URL(newsLink);
                    newsSource = url.hostname.replace('www.', '').toUpperCase(); // Trim 'www.' and capitalize
                } catch (error) {
                    console.warn("Invalid URL for news source:", newsLink);
                }

                // Debugging: Log found details
                console.log("Tooltip Image URL:", imageUrl);
                console.log("News Source:", newsSource);
                console.log("News Link:", newsLink);

                // Remove existing tooltips to prevent duplicates
                let existingTooltip = document.querySelector('.news-tooltip');
                if (existingTooltip) existingTooltip.remove();

                // Create tooltip element
                let tooltip = document.createElement('div');
                tooltip.className = 'news-tooltip';
                tooltip.style.position = 'absolute';
                tooltip.style.backgroundColor = 'white';
                tooltip.style.border = '2px solid black';
                tooltip.style.padding = '12px'; // Increased padding for a larger feel
                tooltip.style.fontSize = '16px'; // Larger text for better readability
                tooltip.style.maxWidth = '300px'; // Slightly larger width
                tooltip.style.wordWrap = 'break-word';
                tooltip.style.zIndex = '1000';
                tooltip.style.boxShadow = '2px 2px 10px rgba(0,0,0,0.3)';
                tooltip.style.borderRadius = '5px';
                tooltip.style.transition = 'opacity 0.2s ease-in-out';
                tooltip.style.opacity = '0';
                tooltip.style.display = 'flex';
                tooltip.style.flexDirection = 'column';
                tooltip.style.alignItems = 'center';
                tooltip.style.textAlign = 'center';

                // Add image if available
                if (imageUrl) {
                    let img = document.createElement('img');
                    img.src = imageUrl;
                    img.style.width = '100%';
                    img.style.maxHeight = '180px'; // Slightly taller image
                    img.style.objectFit = 'cover';
                    img.style.borderBottom = '2px solid black';
                    img.style.marginBottom = '8px';
                    tooltip.appendChild(img);
                }

                // Add summary text
                let text = document.createElement('p');
                text.innerText = summary;
                text.style.padding = '8px';
                text.style.fontSize = '16px';
                text.style.lineHeight = '1.4';
                tooltip.appendChild(text);

                // Add news source link at bottom
                let sourceLink = document.createElement('a');
                sourceLink.href = newsLink;
                sourceLink.innerText = newsSource;
                sourceLink.style.fontSize = '8px';
                sourceLink.style.textTransform = 'uppercase';
                sourceLink.style.color = '#555';
                sourceLink.style.fontWeight = 'bold';
                sourceLink.style.textDecoration = 'none';
                sourceLink.style.marginTop = '5px';
                sourceLink.target = "_blank"; // Open in new tab
                tooltip.appendChild(sourceLink);

                document.body.appendChild(tooltip);

                // Position tooltip near the mouse
                function positionTooltip(event) {
                    let mouseX = event.pageX + 10; // Offset tooltip slightly from cursor
                    let mouseY = event.pageY + 10;

                    // Ensure tooltip does not go off-screen
                    if (mouseX + tooltip.offsetWidth > window.innerWidth) {
                        mouseX = event.pageX - tooltip.offsetWidth - 10; // Move left
                    }
                    if (mouseY + tooltip.offsetHeight > window.innerHeight) {
                        mouseY = event.pageY - tooltip.offsetHeight - 10; // Move up
                    }

                    tooltip.style.left = mouseX + 'px';
                    tooltip.style.top = mouseY + 'px';
                    tooltip.style.opacity = '1'; // Fade-in effect
                }

                // Position tooltip on hover and move with the cursor
                positionTooltip(e);
                e.target.addEventListener('mousemove', positionTooltip);

                // Remove tooltip on mouse leave
                e.target.addEventListener('mouseleave', function () {
                    tooltip.style.opacity = '0';
                    setTimeout(() => tooltip.remove(), 200); // Delay removal for fade-out effect
                });
            });
        });
    });
</script>







<?php
    endwhile;
else :
    echo '<p>No content found for the homepage.</p>';
endif;

get_footer();