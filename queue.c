#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "queue.h"
#include "random.h"

#define Q_MERGE_TREELIKE (0)
#define Q_MERGE_SEQUENTIAL (1)

#ifndef Q_MERGE
#define Q_MERGE Q_MERGE_TREELIKE
#endif

/* Notice: sometimes, Cppcheck would find the potential NULL pointer bugs,
 * but some of them cannot occur. You can suppress them by adding the
 * following line.
 *   cppcheck-suppress nullPointer
 */

/* Create an empty queue */
struct list_head *q_new()
{
    struct list_head *p = malloc(sizeof(struct list_head));

    if (!p)
        return p;

    INIT_LIST_HEAD(p);
    return p;
}

/* Free all storage used by queue */
void q_free(struct list_head *head)
{
    if (!head)
        return;

    /* Cppcheck workaround */
    element_t *entry = NULL, *safe = NULL;
    list_for_each_entry_safe(entry, safe, head, list) {
        q_release_element(entry);
    }

    free(head);
}

/* Insert an element at head of queue */
bool q_insert_head(struct list_head *head, char *s)
{
    if (!head)
        return false;

    char *cp = strdup(s);
    if (!cp)
        return false;

    element_t *entry = malloc(sizeof(element_t));
    if (!entry) {
        free(cp);
        return false;
    }
    entry->value = cp;

    list_add(&entry->list, head);
    return true;
}

/* Insert an element at tail of queue */
bool q_insert_tail(struct list_head *head, char *s)
{
    if (!head)
        return false;

    char *cp = strdup(s);
    if (!cp)
        return false;

    element_t *entry = malloc(sizeof(element_t));
    if (!entry) {
        free(cp);
        return false;
    }
    entry->value = cp;

    list_add_tail(&entry->list, head);
    return true;
}

/* Remove an element from head of queue */
element_t *q_remove_head(struct list_head *head, char *sp, size_t bufsize)
{
    if (!head || list_empty(head))
        return NULL;

    element_t *front = list_first_entry(head, element_t, list);
    list_del(&front->list);

    if (sp) {
        strncpy(sp, front->value, bufsize - 1);
        sp[bufsize - 1] = '\0';
    }

    return front;
}

/* Remove an element from tail of queue */
element_t *q_remove_tail(struct list_head *head, char *sp, size_t bufsize)
{
    if (!head || list_empty(head))
        return NULL;

    element_t *tail = list_last_entry(head, element_t, list);
    list_del(&tail->list);

    if (sp) {
        strncpy(sp, tail->value, bufsize - 1);
        sp[bufsize - 1] = '\0';
    }

    return tail;
}

/* Return number of elements in queue */
int q_size(struct list_head *head)
{
    if (!head || list_empty(head))
        return 0;

    int size = 0;
    struct list_head *node;
    list_for_each(node, head)
        ++size;

    return size;
}

/* Delete the middle node in queue */
bool q_delete_mid(struct list_head *head)
{
    if (!head || list_empty(head))
        return false;

    struct list_head *front, *tail;
    for (front = head->next, tail = head->prev;
         front != tail && tail->next != front;
         front = front->next, tail = tail->prev)
        ;
    list_del(front);
    q_release_element(list_entry(front, element_t, list));

    return true;
}

/* Delete all nodes that have duplicate string */
bool q_delete_dup(struct list_head *head)
{
    if (!head || list_empty(head))
        return false;

    bool last_dup = false;
    element_t *entry = NULL, *safe = NULL;
    list_for_each_entry_safe(entry, safe, head, list) {
        bool cur_dup =
            (&safe->list != head && !strcmp(entry->value, safe->value));

        if (cur_dup || last_dup) {
            list_del(&entry->list);
            q_release_element(entry);
            last_dup = cur_dup;
        }
    }
    return true;
}

/* Swap every two adjacent nodes */
void q_swap(struct list_head *head)
{
    if (!head || list_empty(head))
        return;

    struct list_head *l1, *l2;
    list_for_each_safe(l1, l2, head) {
        if (l2 != head) {
            list_del(l1);
            list_add(l1, l2);
            l2 = l1->next;
        }
    }
}

#define list_for_each_prev_safe(pos, n, head) \
    for (pos = (head)->prev, n = pos->prev; pos != head; pos = n, n = pos->prev)

/* Reverse elements in queue */
void q_reverse(struct list_head *head)
{
    if (!head || list_empty(head) || list_is_singular(head))
        return;

    const struct list_head *tail = head->prev;
    struct list_head *node, *safe;
    list_for_each_prev_safe(node, safe, head)
    {
        if (node == tail)
            continue;
        // move current element to tail->next
        list_move_tail(node, head);
    }
}

/* Reverse the nodes of the list k at a time */
void q_reverseK(struct list_head *head, int k)
{
    if (!head || list_empty(head) || list_is_singular(head) || k == 1)
        return;

    int counter = 0;
    LIST_HEAD(tmp);
    LIST_HEAD(final);
    struct list_head *node, *safe;

    list_for_each_safe(node, safe, head) {
        if (++counter == k) {
            list_cut_position(&tmp, head, node);
            q_reverse(&tmp);
            list_splice_tail_init(&tmp, &final);
            counter = 0;
        }
    }
    list_splice(&final, head);
}

/**
 * list_prev_entry - get the prev element in list
 * @pos:	the type * to cursor
 * @member:	the name of the list_head within the struct.
 */
#define list_prev_entry(pos, member) \
    list_entry((pos)->member.prev, typeof(*(pos)), member)

/* Remove every node which has a node with a strictly less value anywhere to
 * the right side of it */
int q_ascend(struct list_head *head)
{
    if (!head || list_empty(head))
        return 0;
    if (list_is_singular(head))
        return 1;

    int size = 1;
    element_t *tail = list_last_entry(head, element_t, list);
    const char *bound_val = tail->value;
    element_t *node = list_prev_entry(tail, list),
              *safe = list_prev_entry(node, list);

    for (; &node->list != head;
         node = safe, safe = list_prev_entry(node, list)) {
        if (strcmp(node->value, bound_val) > 0) {
            list_del(&node->list);
            q_release_element(node);
        } else {
            ++size;
            bound_val = node->value;
        }
    }
    return size;
}

/* Remove every node which has a node with a strictly greater value anywhere to
 * the right side of it */
int q_descend(struct list_head *head)
{
    if (!head || list_empty(head))
        return 0;
    if (list_is_singular(head))
        return 1;

    int size = 1;
    element_t *tail = list_last_entry(head, element_t, list);
    const char *bound_val = tail->value;
    element_t *node = list_prev_entry(tail, list),
              *safe = list_prev_entry(node, list);

    for (; &node->list != head;
         node = safe, safe = list_prev_entry(node, list)) {
        if (strcmp(node->value, bound_val) < 0) {
            list_del(&node->list);
            q_release_element(node);
        } else {
            ++size;
            bound_val = node->value;
        }
    }
    return size;
}

/**
 * @brief Merges two sorted lists into one without any heap allocation.
 *
 * This function merges two sorted lists (l1 and l2) into a single sorted list
 * based on string values. It assumes that at least one list pointer is non-NULL
 * and does not perform any dynamic memory allocation.
 *
 * Special cases:
 * - If either l1 or l2 is NULL, the function returns the size of the non-NULL
 * list.
 * - If one (or two) of the lists is (are) empty, the function splices the
 * non-empty list into l1 (if l1 is empty, l2 is spliced into l1) to avoid a
 * self-splice, then returns the resulting size.
 *
 * The merge process uses a temporary dummy list. It repeatedly compares the
 * first elements of both lists, moves the appropriate element (based on the
 * 'descend' flag) to the dummy list, and finally appends any remaining
 * elements. The dummy list is then spliced back into l1.
 *
 * @param l1 Pointer to the first queue.
 * @param l2 Pointer to the second queue.
 * @param descend If true, sorts in descending order; otherwise, ascending.
 * @return int The total number of elements in the merged list.
 */
static int q_merge_two(struct list_head *l1, struct list_head *l2, bool descend)
{
    /* no heap allocation; return size if one list is NULL */
    if (!l1 || !l2)
        return q_size(l1 ? l1 : l2);

    /* if a list is empty, splice l2 into l1 (if l1 is empty) to avoid
     * self-splice */
    if (list_empty(l1) || list_empty(l2)) {
        if (list_empty(l1))
            list_splice(l2, l1);
        return q_size(l1);
    }

    int size = 0;
    LIST_HEAD(dummy);
    for (; !list_empty(l1) && !list_empty(l2); ++size) {
        element_t *node1 = list_first_entry(l1, element_t, list);
        element_t *node2 = list_first_entry(l2, element_t, list);
        int cmp = strcmp(node1->value, node2->value);
        element_t *next =
            descend ? (cmp > 0 ? node1 : node2) : (cmp > 0 ? node2 : node1);
        list_move_tail(&next->list, &dummy);
    }

    struct list_head *valid = list_empty(l1) ? l2 : l1;
    size += q_size(valid);
    /* use init for list splice (avoid valid is l1) */
    list_splice_tail_init(valid, &dummy);
    list_splice(&dummy, l1);
    return size;
}

/**
 * list_iter_n - Iterates through the list starting from a given position.
 *
 * @pos: The current position in the list from which iteration starts.
 * @head: The head of the list to ensure the iteration stops at the list's end.
 * @n: The number of steps to move forward in the list.
 *
 * This function moves the position forward by 'n' steps in the list.
 * It stops either when 'n' steps have been taken or when the end of the list
 * (head) is reached.
 *
 * Return: The new position after iterating 'n' steps, or the list's head if the
 * end is reached.
 */
static inline struct list_head *list_iter_n(struct list_head *pos,
                                            struct list_head *head,
                                            int n)
{
    /* TODO: should we add unlikely here? */
    while (n-- > 0 && pos != head) {
        pos = pos->next;
    }
    return pos;
}

/* Merge all the queues into one sorted queue, which is in ascending/descending
 * order */
int q_merge(struct list_head *head, bool descend)
{
    if (!head || list_empty(head))
        return 0;
    if (list_is_singular(head))
        return q_size(list_first_entry(head, queue_contex_t, chain)->q);

    int ele_count = 0;

#if Q_MERGE == Q_MERGE_SEQUENTIAL
#pragma message("q_merge: using sequential method")
    struct list_head *first = head->next;
    queue_contex_t *first_q = list_entry(first, queue_contex_t, chain);

    /* sequential merging */
    for (struct list_head *next = first->next; next != head;
         next = next->next) {
        queue_contex_t *next_q = list_entry(next, queue_contex_t, chain);
        ele_count = q_merge_two(first_q->q, next_q->q, descend);
    }

#elif Q_MERGE == Q_MERGE_TREELIKE
#pragma message("q_merge: using tree-like method")
    const int q_count = q_size(head);

    /* tree-like merging */
    for (int iter_diff = 1; iter_diff < q_count; iter_diff <<= 1) {
        /* start from the first node */
        struct list_head *ctx1_node = head->next;
        /* the first q_contex_t note as bias 0 (index 0) */
        for (int bias = 0; bias < q_count; bias += (iter_diff << 1)) {
            /* break if ctx1 or ctx2 meet queue chain head */
            if (ctx1_node == head)
                break;
            struct list_head *ctx2_node =
                list_iter_n(ctx1_node, head, iter_diff);
            if (ctx2_node == head)
                break;

            queue_contex_t *ctx1 = list_entry(ctx1_node, queue_contex_t, chain);
            queue_contex_t *ctx2 = list_entry(ctx2_node, queue_contex_t, chain);
            ele_count = q_merge_two(ctx1->q, ctx2->q, descend);

            /* optional */
            // ctx1->size = ele_count;
            // ctx2->size = 0;

            if (bias + (iter_diff << 1) < q_count)
                ctx1_node = list_iter_n(ctx1_node, head, iter_diff << 1);
        }
    }
#endif
    return ele_count;
}

static void list_cut_n(struct list_head *dest, struct list_head *src, int n)
{
    if (n <= 0 || list_empty(src)) {
        INIT_LIST_HEAD(dest);
        return;
    }
    struct list_head *cut = list_iter_n(src->next, src, n);
    list_cut_position(dest, src, cut->prev);
}

/* Sort elements of queue in ascending/descending order */
void q_sort(struct list_head *head, bool descend)
{
    if (!head || list_empty(head) || list_is_singular(head))
        return;

    const int total = q_size(head);
    for (int iter_diff = 1; iter_diff < total; iter_diff <<= 1) {
        LIST_HEAD(new_head);
        while (!list_empty(head)) {
            LIST_HEAD(left);
            LIST_HEAD(right);

            list_cut_n(&left, head, iter_diff);
            list_cut_n(&right, head, iter_diff);

            q_merge_two(&left, &right, descend);
            list_splice_tail(&left, &new_head);
        }
        list_splice_tail(&new_head, head);
    }
}

/* ref: https://doi.org/10.48550/arXiv.1805.10941, OpenBSD method */
#ifndef Q_SHUFFLE_BIAS
static uint32_t unbias(uint32_t upper, rand_func_t func)
{
    // Calculate threshold value to eliminate bias.
    uint32_t t = (-upper) % upper;
    uint32_t x;
    do {
        func((uint8_t *) &x, sizeof(uint32_t));
    } while (x < t);
    return x % upper;
}
#endif

/* Shuffle the queue */
void q_shuffle(struct list_head *head)
{
    if (!head || list_empty(head) || list_is_singular(head))
        return;

    const int total = q_size(head);
    LIST_HEAD(dummy);

    for (int i = total; i > 0; --i) {
        /* generate a random number between 0 to i - 1*/
        uint32_t j;

#ifdef Q_SHUFFLE_BIAS
#pragma message("q_shuffle: using bias method")
        prng_funcs[prng]((uint8_t *) &j, sizeof(uint32_t));
        j = j % i;
#else
#pragma message("q_shuffle: using unbias method")
        j = unbias(i, prng_funcs[prng]);
#endif

        struct list_head *node = list_iter_n(head->next, head, (int) j);
        list_move(node, &dummy);
    }
    list_splice(&dummy, head);
}
