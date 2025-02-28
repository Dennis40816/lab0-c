#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "queue.h"

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
    list_for_each_entry_safe (entry, safe, head, list) {
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
    list_for_each (node, head)
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
    list_for_each_entry_safe (entry, safe, head, list) {
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
    list_for_each_safe (l1, l2, head) {
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

    list_for_each_safe (node, safe, head) {
        if (++counter == k) {
            list_cut_position(&tmp, head, node);
            q_reverse(&tmp);
            list_splice_tail_init(&tmp, &final);
            counter = 0;
        }
    }
    list_splice(&final, head);
}

/* Sort elements of queue in ascending/descending order */
void q_sort(struct list_head *head, bool descend) {}

/**
 * list_prev_entry - get the prev element in list
 * @pos:	the type * to cursor
 * @member:	the name of the list_head within the struct.
 */
#define list_prev_entry(pos, member) \
    list_entry((pos)->member.prev, typeof(*(pos)), member)

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

/* Merge all the queues into one sorted queue, which is in ascending/descending
 * order */
int q_merge(struct list_head *head, bool descend)
{
    // https://leetcode.com/problems/merge-k-sorted-lists/
    return 0;
}
